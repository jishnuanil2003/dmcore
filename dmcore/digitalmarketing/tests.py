from django.conf import settings
import base64
import hashlib
import hmac
import io
import json
import socket
import smtplib
from datetime import timedelta
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

from django.core import signing
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.core.management import call_command, CommandError
from django.test import Client, TestCase, override_settings
from django.utils import timezone

from .models import (
    BusinessRegister_Details,
    ClientTask_Register,
    ClientRegister,
    DataBank,
    EmployeeRegister_Details,
    LeadCategory_Register,
    LeadConfused,
    LeadDetails,
    LeadField_Register,
    Leads,
    LogRegister_Details,
    TaskAssign,
    WorkRegister,
)
from .utils import (
    COURSE_QUESTION_ID,
    INTERVIEW_TOKEN_MAX_AGE,
    make_interview_link,
    make_interview_token,
    get_lead_missing_interview_questions,
)
from .validators import (
    is_valid_email,
    is_valid_phone,
    normalize_phone_e164,
    mask_email,
    mask_phone,
)
from .sms import LocmemSMSBackend, locmem_outbox


@override_settings(
    AI_HR_API_KEY='test-api-key',
    AI_HR_URL='https://interviews.example.test/',
    INTERVIEW_LINK='https://interviews.example.test/',
    INTERVIEW_LINK_SIGN=True,
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    DEFAULT_FROM_EMAIL='hr@example.test',
    SMS_BACKEND='locmem',
)
class InterviewAPITests(TestCase):
    def setUp(self):
        LocmemSMSBackend.reset()
        self.company = BusinessRegister_Details.objects.create(company_code='TEST001', company_name='Test Co')
        self.client_record = ClientRegister.objects.create(company=self.company, client_name='Client')
        self.work = WorkRegister.objects.create(company=self.company, client=self.client_record)
        self.category = LeadCategory_Register.objects.create(collection_for='Hiring')
        self.login = LogRegister_Details.objects.create(log_username='manager', position='Data_Manager')
        self.manager = EmployeeRegister_Details.objects.create(login=self.login, company=self.company, name='Manager')
        self.lead = Leads.objects.create(
            work=self.work, collected_by=self.manager, lead_category=self.category,
            name='Candidate One', email='candidate@example.test', contact='9876543210',
            source='Campus Drive',
        )
        LeadDetails.objects.create(lead=self.lead, field_name='Course', field_data='Computer Science')
        self.field = LeadField_Register.objects.create(
            work=self.work, lead_category=self.category,
            name='Experience', description='Describe your experience', question_id=4
        )
        self.empty_description = LeadField_Register.objects.create(work=self.work, name='Ignored', description='')
        self.other_work = WorkRegister.objects.create(company=self.company, client=self.client_record)
        self.other_field = LeadField_Register.objects.create(work=self.other_work, name='Private', description='Other work')
        self.token = make_interview_token(self.lead.pk)
        self.headers = {'HTTP_X_API_KEY': 'test-api-key', 'HTTP_X_INTERVIEW_TOKEN': self.token}

    def request(self, path, method='get', data=None, headers=None):
        return getattr(self.client, method)(path, data=data, content_type='application/json', **(headers or self.headers))

    def test_session_valid_and_key_errors(self):
        response = self.request('/api/interview/session/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['candidate']['name'], 'Candidate One')
        self.assertEqual(response.json()['questions'], [{'question_id': 4, 'field_key': 'role_applied'}])
        for key_headers in ({'HTTP_X_INTERVIEW_TOKEN': self.token},
                            {'HTTP_X_API_KEY': 'wrong', 'HTTP_X_INTERVIEW_TOKEN': self.token}):
            self.assertEqual(self.request('/api/interview/session/', headers=key_headers).status_code, 401)

    def test_session_returns_only_mapped_questions_in_id_order(self):
        self.empty_description.question_id = 15
        self.empty_description.save(update_fields=['question_id'])
        LeadField_Register.objects.create(work=self.work, name='Unmapped', description='Not played')
        response = self.request('/api/interview/session/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['questions'], [
            {'question_id': 4, 'field_key': 'role_applied'},
            {'question_id': 15, 'field_key': 'notice_period'},
        ])

    def test_session_returns_empty_for_unmapped_lead_and_logs_warning(self):
        lead = Leads.objects.create(
            work=self.other_work, collected_by=self.manager, name='Unmapped Candidate',
            email='unmapped@example.test', contact='9876543210', source='Campus Drive'
        )
        LeadDetails.objects.create(lead=lead, field_name='Course', field_data='B.Tech')
        token = make_interview_token(lead.pk)
        with self.assertLogs('digitalmarketing.views', level='WARNING') as logs:
            response = self.request('/api/interview/session/', headers={
                'HTTP_X_API_KEY': 'test-api-key', 'HTTP_X_INTERVIEW_TOKEN': token,
            })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['questions'], [])
        self.assertIn(f'lead_id={lead.pk}', logs.output[0])

    def test_question_id_is_unique_per_work_and_validated(self):
        duplicate = LeadField_Register(
            work=self.work, name='Duplicate', question_id=4,
        )
        with self.assertRaises(ValidationError):
            duplicate.full_clean()

        other_work_mapping = LeadField_Register(
            work=self.other_work, name='Same ID in another work', question_id=4,
        )
        other_work_mapping.full_clean()

    def test_add_field_rejects_duplicate_question_with_clear_error(self):
        response = self.client.post('/add-field/', {
            'category_id': self.category.pk,
            'field_name': 'Duplicate mapping',
            'description': 'Duplicate question test',
            'client_id': self.client_record.pk,
            'work_id': self.work.pk,
            'question_id': '4',
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn('already assigned to another field', response.json()['message'])

    def test_existing_unmapped_field_can_be_mapped_and_invalid_id_is_rejected(self):
        response = self.client.post('/edit-field/', {
            'field_id': self.empty_description.pk,
            'field_name': self.empty_description.name,
            'description': self.empty_description.description,
            'question_id': '15',
        })
        self.assertEqual(response.status_code, 200)
        self.empty_description.refresh_from_db()
        self.assertEqual(self.empty_description.question_id, 15)

        invalid = self.client.post('/edit-field/', {
            'field_id': self.empty_description.pk,
            'field_name': self.empty_description.name,
            'description': self.empty_description.description,
            'question_id': '25',
        })
        self.assertEqual(invalid.status_code, 400)
        self.assertIn('valid interview question', invalid.json()['message'])

    def test_token_errors_and_unknown_lead(self):
        for token, status in (('', 400), ('bad.token', 400)):
            headers = {'HTTP_X_API_KEY': 'test-api-key', 'HTTP_X_INTERVIEW_TOKEN': token}
            self.assertEqual(self.request('/api/interview/session/', headers=headers).status_code, status)
        expired = signing.dumps({'lead': self.lead.pk}, salt='interview-link')
        with patch('time.time', return_value=timezone.now().timestamp() + INTERVIEW_TOKEN_MAX_AGE + 100):
            response = self.request('/api/interview/session/', headers={
                'HTTP_X_API_KEY': 'test-api-key', 'HTTP_X_INTERVIEW_TOKEN': expired,
            })
        self.assertEqual(response.status_code, 410)
        unknown = signing.dumps({'lead': 999999}, salt='interview-link')
        response = self.request('/api/interview/session/', headers={
            'HTTP_X_API_KEY': 'test-api-key', 'HTTP_X_INTERVIEW_TOKEN': unknown,
        })
        self.assertEqual(response.status_code, 404)

    def test_expired_token_rejected_on_all_endpoints(self):
        expired = signing.dumps({'lead': self.lead.pk}, salt='interview-link')
        with patch('time.time', return_value=timezone.now().timestamp() + INTERVIEW_TOKEN_MAX_AGE + 100):
            expired_token = expired
            for path, method, data in (
                ('/api/interview/session/', 'get', None),
                ('/api/interview/answer/', 'post', {'answers': [{'question_id': 4, 'answer': 'Answer'}]}),
                ('/api/interview/complete/', 'post', {}),
            ):
                headers = {'HTTP_X_API_KEY': 'test-api-key', 'HTTP_X_INTERVIEW_TOKEN': expired_token}
                self.assertEqual(self.request(path, method, data, headers=headers).status_code, 410)

    def test_answer_endpoint_validates_and_stores_and_updates(self):
        for payload, error in (
            ({'answers': 'not-a-list'}, 'answers must be a list'),
            ({'answers': ['not-a-dict']}, 'Each answer must include question_id and answer'),
            ({'answers': [{'question_id': 99, 'answer': 'bad'}]}, 'Unknown question id: 99'),
            ({'answers': [{'question_id': 15, 'answer': 'unmapped'}]}, 'Question id 15 is not mapped to this lead'),
            ({'answers': [{'question_id': 4, 'answer': ''}]}, 'Answer must be a non-empty string'),
        ):
            response = self.request('/api/interview/answer/', 'post', payload)
            self.assertEqual(response.status_code, 400)
            self.assertIn(error, response.json()['error'])

        payload = {'answers': [{'question_id': 4, 'answer': 'a' * 900}]}
        response = self.request('/api/interview/answer/', 'post', payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'success': True})
        self.assertEqual(LeadDetails.objects.get(lead=self.lead, field_name='Experience').field_data, 'a' * 855)

        update_payload = {'answers': [{'question_id': 4, 'answer': 'Updated'}]}
        response = self.request('/api/interview/answer/', 'post', update_payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(LeadDetails.objects.filter(lead=self.lead, field_name='Experience').count(), 1)
        self.assertEqual(LeadDetails.objects.get(lead=self.lead, field_name='Experience').field_data, 'Updated')

    def test_complete_endpoint_marks_interview_completed_and_prevents_replay(self):
        response = self.request('/api/interview/complete/', 'post', {})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'success': True})
        self.assertTrue(LeadDetails.objects.filter(lead=self.lead, field_name='AI Interview Status', field_data='Completed').exists())

        for path, method, data in (
            ('/api/interview/session/', 'get', None),
            ('/api/interview/answer/', 'post', {'answers': [{'question_id': 4, 'answer': 'Replay'}]}),
        ):
            self.assertEqual(self.request(path, method, data).status_code, 409)
        self.assertEqual(self.request('/api/interview/complete/', 'post', {}).status_code, 200)


@override_settings(
    AI_HR_API_KEY='test-api-key',
    AI_HR_URL='https://interviews.example.test/',
    INTERVIEW_LINK='https://interviews.example.test/',
    INTERVIEW_LINK_SIGN=True,
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    DEFAULT_FROM_EMAIL='hr@example.test',
    SMS_BACKEND='locmem',
)
class SendInterviewTests(TestCase):
    def setUp(self):
        LocmemSMSBackend.reset()
        self.company = BusinessRegister_Details.objects.create(company_code='SEND001', company_name='Test Co')
        self.login = LogRegister_Details.objects.create(log_username='manager', position='Data_Manager')
        self.manager = EmployeeRegister_Details.objects.create(login=self.login, company=self.company, name='Manager')
        self.work = WorkRegister.objects.create(company=self.company)
        self.client_task = ClientTask_Register.objects.create(
            company=self.company, work=self.work, task_name='Lead Collection'
        )
        self.category = LeadCategory_Register.objects.create(client_task=self.client_task, collection_for='Hiring')
        self.lead = Leads.objects.create(
            collected_by=self.manager, work=self.work, lead_category=self.category,
            name='Candidate One', email='candidate@example.test', contact='9876543210',
            source='Campus Drive',
        )
        LeadDetails.objects.create(lead=self.lead, field_name='Course', field_data='B.Tech')
        LeadField_Register.objects.create(
            work=self.work, lead_category=self.category,
            name='Experience', description='Describe your experience', question_id=4
        )
        self.path = f'/api/leads/{self.lead.pk}/send-interview/'
        self.client = Client(enforce_csrf_checks=True)
        session = self.client.session
        session['did'] = 'manager'
        session.save()

    def csrf_post(self, path):
        self.client.get('/databank/')
        token = self.client.cookies['csrftoken'].value
        return self.client.post(path, HTTP_X_CSRFTOKEN=token)

    def test_logged_out_and_csrf_required(self):
        anonymous = Client(enforce_csrf_checks=True)
        self.assertEqual(anonymous.post(self.path).status_code, 403)
        self.assertEqual(self.client.post(self.path).status_code, 403)

    def test_not_confused_and_success_with_short_link(self):
        # Lead not confused -> 400
        self.assertEqual(self.csrf_post(self.path).status_code, 400)
        LeadConfused.objects.create(lead=self.lead, executive_id=self.manager)

        response = self.csrf_post(self.path)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['channel'], 'email')
        self.assertIn('Email sent to', response.json()['message'])
        self.assertIn('c***@example.test', response.json()['message'])

        from django.core import mail
        self.assertEqual(len(mail.outbox), 1)
        message = mail.outbox[0]
        self.assertEqual(message.to, ['candidate@example.test'])
        company_name = getattr(settings, 'COMPANY_NAME', 'Altos Technologies')
        self.assertEqual(message.subject, f"Your interview invitation from {company_name}")
        self.assertIn('?token=', message.body)
        self.assertNotIn('?data=', message.body)
        self.assertNotIn('&sig=', message.body)

        # 10-minute resend guard
        self.assertEqual(self.csrf_post(self.path).status_code, 409)

    def test_all_filled_returns_422(self):
        LeadConfused.objects.create(lead=self.lead, executive_id=self.manager)
        # Fill the remaining missing custom field
        LeadDetails.objects.create(lead=self.lead, field_name='Experience', field_data='5 years')
        response = self.csrf_post(self.path)
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()['message'], 'All fields are already filled, there is nothing to ask')

    def test_smtp_dns_failure_returns_actionable_error(self):
        LeadConfused.objects.create(lead=self.lead, executive_id=self.manager)
        with patch('django.core.mail.EmailMultiAlternatives.send', side_effect=socket.gaierror('getaddrinfo failed')):
            response = self.csrf_post(self.path)
        self.assertEqual(response.status_code, 502)
        self.assertIn('Could not resolve the Gmail SMTP server', response.json()['message'])


class TaskAssignStringTests(TestCase):
    def test_task_assign_str(self):
        company = BusinessRegister_Details.objects.create(company_code='TASK001', company_name='Task Co')
        login = LogRegister_Details.objects.create(log_username='exec', position='Executive')
        executive = EmployeeRegister_Details.objects.create(login=login, company=company, name='Exec')
        task = TaskAssign.objects.create(executive=executive, target=10)
        self.assertEqual(str(task), f'TaskAssign #{task.pk}')


class DataBankLeadsAPITests(TestCase):
    def setUp(self):
        self.company = BusinessRegister_Details.objects.create(company_code='DB001', company_name='DataBank Co')
        self.login = LogRegister_Details.objects.create(log_username='manager2', position='Data_Manager')
        self.manager = EmployeeRegister_Details.objects.create(login=self.login, company=self.company, name='Manager 2')
        self.lead = Leads.objects.create(collected_by=self.manager, name='DB Candidate', email='db@example.test', contact='9876543210')
        self.client = Client()
        session = self.client.session
        session['did'] = 'manager2'
        session.save()

    def test_databank_api_returns_leads(self):
        res = self.client.get('/api/leads/', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data['count'], 1)
        self.assertEqual(data['results'][0]['name'], 'DB Candidate')


class HardeningAndMappingTests(TestCase):
    def setUp(self):
        self.company = BusinessRegister_Details.objects.create(company_code='MAP001', company_name='Map Co')
        self.client_record = ClientRegister.objects.create(company=self.company, client_name='Client')
        self.work = WorkRegister.objects.create(company=self.company, client=self.client_record)
        self.category = LeadCategory_Register.objects.create(collection_for='Interview')
        self.exec_login = LogRegister_Details.objects.create(log_username='exec@example.test', position='Executive')
        self.executive = EmployeeRegister_Details.objects.create(
            login=self.exec_login, company=self.company, name='Executive One'
        )

    def test_map_default_fields_command_maps_client_fields(self):
        names_and_expected = [
            ('Highest qualification', 5),
            ('skills', 14),
            ('Notice period', 15),
            ('salary', 16),
        ]
        created_fields = [
            LeadField_Register.objects.create(
                work=self.work, client=self.client_record, lead_category=self.category, name=name
            )
            for name, _ in names_and_expected
        ]
        call_command('map_default_fields', stdout=io.StringIO())
        for field, (_name, expected_qid) in zip(created_fields, names_and_expected):
            field.refresh_from_db()
            self.assertEqual(field.question_id, expected_qid)


@override_settings(
    AI_HR_API_KEY='test-api-key',
    AI_HR_URL='https://interviews.example.test/',
    INTERVIEW_LINK='https://interviews.example.test/',
    INTERVIEW_LINK_SIGN=True,
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    DEFAULT_FROM_EMAIL='hr@example.test',
    SMS_BACKEND='locmem',
    INTERVIEW_PREFERRED_CHANNEL='email',
    DEFAULT_PHONE_COUNTRY_CODE='91',
)
class NewRequirementsTests(TestCase):
    """
    Comprehensive tests covering all requirements 1-6.
    """

    def setUp(self):
        LocmemSMSBackend.reset()
        self.company = BusinessRegister_Details.objects.create(company_code='NEW001', company_name='New Co')
        self.client_record = ClientRegister.objects.create(company=self.company, client_name='Client')
        self.work = WorkRegister.objects.create(company=self.company, client=self.client_record)
        self.client_task = ClientTask_Register.objects.create(
            company=self.company, work=self.work, task_name='Lead Collection'
        )
        self.category = LeadCategory_Register.objects.create(client_task=self.client_task, collection_for='Engineering')
        self.login = LogRegister_Details.objects.create(log_username='datamanager', position='Data_Manager')
        self.manager = EmployeeRegister_Details.objects.create(login=self.login, company=self.company, name='Data Manager')

        self.lead = Leads.objects.create(
            work=self.work, collected_by=self.manager, lead_category=self.category,
            name='Alice Smith', email='alice@example.test', contact='9876543210',
            source='Campus Drive',
        )
        LeadDetails.objects.create(lead=self.lead, field_name='Course', field_data='B.Tech')
        LeadConfused.objects.create(lead=self.lead, executive_id=self.manager)

        self.token = make_interview_token(self.lead.pk)
        self.headers = {'HTTP_X_API_KEY': 'test-api-key', 'HTTP_X_INTERVIEW_TOKEN': self.token}

        self.client = Client(enforce_csrf_checks=True)
        session = self.client.session
        session['did'] = 'datamanager'
        session.save()

    def csrf_post(self, path):
        self.client.get('/databank/')
        token = self.client.cookies['csrftoken'].value
        return self.client.post(path, HTTP_X_CSRFTOKEN=token)

    # --- 1. QUESTIONS TESTS ---
    def test_questions_all_filled_gives_empty_list_and_send_returns_422(self):
        # All default fields filled, no custom fields -> questions is empty
        q = get_lead_missing_interview_questions(self.lead)
        self.assertEqual(q, [])
        res = self.csrf_post(f'/api/leads/{self.lead.pk}/send-interview/')
        self.assertEqual(res.status_code, 422)
        self.assertEqual(res.json()['message'], 'All fields are already filled, there is nothing to ask')

    def test_questions_only_notice_period_missing(self):
        # All default fields filled, custom field notice period (15) mapped but no value
        LeadField_Register.objects.create(work=self.work, name='Notice period', question_id=15)
        q = get_lead_missing_interview_questions(self.lead)
        self.assertEqual(q, [{'question_id': 15, 'field_key': 'notice_period'}])

    def test_questions_default_fields_missing_gives_1_2_3_19_plus_custom(self):
        empty_lead = Leads.objects.create(
            work=self.work, collected_by=self.manager, lead_category=self.category,
            name='', email='', contact='', source=''
        )
        LeadField_Register.objects.create(work=self.work, name='Notice period', question_id=15)
        q = get_lead_missing_interview_questions(empty_lead)
        qids = [item['question_id'] for item in q]
        self.assertEqual(qids, [1, 2, 3, 15, 19])

    def test_questions_whitespace_counts_as_empty(self):
        ws_lead = Leads.objects.create(
            work=self.work, collected_by=self.manager, lead_category=self.category,
            name='   ', email='  \t ', contact='   ', source='   '
        )
        LeadDetails.objects.create(lead=ws_lead, field_name='Course', field_data='   ')
        q = get_lead_missing_interview_questions(ws_lead)
        qids = [item['question_id'] for item in q]
        self.assertEqual(qids, [1, 2, 3, 19])

    def test_questions_conflict_case_on_id_6(self):
        # Custom field mapped to question_id 6 (e.g. Major)
        LeadField_Register.objects.create(work=self.work, name='Major', question_id=6)
        # Case A: Course is filled ('B.Tech'), but custom 'Major' is empty -> 6 is needed
        q = get_lead_missing_interview_questions(self.lead)
        qids = [item['question_id'] for item in q]
        self.assertEqual(qids, [6])
        # Case B: Both Course and Major are filled -> 6 is not needed
        LeadDetails.objects.create(lead=self.lead, field_name='Major', field_data='Computer Science')
        q = get_lead_missing_interview_questions(self.lead)
        self.assertEqual(q, [])

    # --- 2. ANSWERS TESTS ---
    def test_answers_1_2_3_6_saved_and_columns_updated_only_when_empty_and_valid(self):
        candidate = Leads.objects.create(
            work=self.work, collected_by=self.manager, lead_category=self.category,
            name='', email='', contact=''
        )
        token = make_interview_token(candidate.pk)
        headers = {'HTTP_X_API_KEY': 'test-api-key', 'HTTP_X_INTERVIEW_TOKEN': token}

        # 1. Answer question 1 (name)
        res1 = self.client.post('/api/interview/answer/', data=json.dumps({
            'token': token, 'question_id': 1, 'answer': 'Bob Martin'
        }), content_type='application/json', **headers)
        self.assertEqual(res1.status_code, 200)
        candidate.refresh_from_db()
        self.assertEqual(candidate.name, 'Bob Martin')
        self.assertEqual(LeadDetails.objects.get(lead=candidate, field_name='Full Name').field_data, 'Bob Martin')

        # 2. Resend name - never overwrite existing lead column
        res1_resend = self.client.post('/api/interview/answer/', data=json.dumps({
            'token': token, 'question_id': 1, 'answer': 'Robert Martin'
        }), content_type='application/json', **headers)
        self.assertEqual(res1_resend.status_code, 200)
        candidate.refresh_from_db()
        self.assertEqual(candidate.name, 'Bob Martin')  # not overwritten
        self.assertEqual(LeadDetails.objects.get(lead=candidate, field_name='Full Name').field_data, 'Robert Martin')  # updated in LeadDetails

        # 3. Answer question 2 with INVALID email - stored in LeadDetails, no 400, column not touched
        res2_bad = self.client.post('/api/interview/answer/', data=json.dumps({
            'token': token, 'question_id': 2, 'answer': 'not-an-email'
        }), content_type='application/json', **headers)
        self.assertEqual(res2_bad.status_code, 200)
        candidate.refresh_from_db()
        self.assertEqual(candidate.email, '')  # column remains empty
        self.assertEqual(LeadDetails.objects.get(lead=candidate, field_name='Email').field_data, 'not-an-email')

        # 4. Answer question 2 with VALID email - column updated
        res2_good = self.client.post('/api/interview/answer/', data=json.dumps({
            'token': token, 'question_id': 2, 'answer': 'bob@example.test'
        }), content_type='application/json', **headers)
        self.assertEqual(res2_good.status_code, 200)
        candidate.refresh_from_db()
        self.assertEqual(candidate.email, 'bob@example.test')

        # 5. Answer question 3 with phone (10 digits) - normalized to E.164 and column updated
        res3 = self.client.post('/api/interview/answer/', data=json.dumps({
            'token': token, 'question_id': 3, 'answer': '9876543210'
        }), content_type='application/json', **headers)
        self.assertEqual(res3.status_code, 200)
        candidate.refresh_from_db()
        self.assertEqual(candidate.contact, '+919876543210')

        # 6. Answer question 6 (Course) - saved in LeadDetails
        res6 = self.client.post('/api/interview/answer/', data=json.dumps({
            'token': token, 'question_id': 6, 'answer': 'Information Technology'
        }), content_type='application/json', **headers)
        self.assertEqual(res6.status_code, 200)
        self.assertEqual(LeadDetails.objects.get(lead=candidate, field_name='Course').field_data, 'Information Technology')

    # --- 3. CONFUSED RULE TESTS ---
    def test_confused_rule_blocked_with_neither_email_nor_phone(self):
        empty_lead = Leads.objects.create(
            work=self.work, collected_by=self.manager, lead_category=self.category,
            name='No Contact Lead', email='', contact=''
        )
        # Model path
        confused_obj = LeadConfused(lead=empty_lead, executive_id=self.manager, reason='Test reason')
        with self.assertRaises(ValidationError) as cm:
            confused_obj.full_clean()
        self.assertIn('Add an email or a phone number before marking this lead as confused', str(cm.exception))

        with self.assertRaises(ValidationError):
            confused_obj.save()

        # View path
        exec_session = self.client.session
        exec_session['eid'] = 'manager'
        exec_session.save()
        res = self.client.post('/excutive-lead-mark-confused/', {
            'lead_id': empty_lead.id,
            'reason': 'Confused reason',
        }, HTTP_REFERER='/lead-list/1/')
        self.assertFalse(LeadConfused.objects.filter(lead=empty_lead).exists())

    def test_confused_rule_allowed_with_either(self):
        # Email only
        email_only = Leads.objects.create(name='Email Only', email='email@test.com', contact='')
        lc_email = LeadConfused.objects.create(lead=email_only, executive_id=self.manager)
        self.assertTrue(lc_email.pk)

        # Phone only
        phone_only = Leads.objects.create(name='Phone Only', email='', contact='9876543210')
        lc_phone = LeadConfused.objects.create(lead=phone_only, executive_id=self.manager)
        self.assertTrue(lc_phone.pk)

    def test_confused_rule_cannot_clear_both_on_confused_lead(self):
        lead = Leads.objects.create(name='Confused', email='conf@test.com', contact='9876543210')
        LeadConfused.objects.create(lead=lead, executive_id=self.manager)
        lead.email = ''
        lead.contact = ''
        with self.assertRaises(ValidationError):
            lead.save()

    # --- 4. SEND CHANNEL TESTS ---
    def test_send_phone_only_goes_by_sms(self):
        phone_lead = Leads.objects.create(
            work=self.work, collected_by=self.manager, lead_category=self.category,
            name='SMS Candidate', email='', contact='9876543210'
        )
        LeadConfused.objects.create(lead=phone_lead, executive_id=self.manager)
        LeadField_Register.objects.create(work=self.work, name='Skills', question_id=14)

        res = self.csrf_post(f'/api/leads/{phone_lead.pk}/send-interview/')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data['channel'], 'sms')
        self.assertIn('+91******3210', data['message'])

        # Check SMS outbox
        self.assertEqual(len(locmem_outbox), 1)
        msg = locmem_outbox[0]
        self.assertEqual(msg['to'], '+919876543210')
        self.assertIn('Hello SMS Candidate, please complete your interview:', msg['message'])
        self.assertIn('?token=', msg['message'])

    def test_send_email_only_goes_by_email(self):
        email_lead = Leads.objects.create(
            work=self.work, collected_by=self.manager, lead_category=self.category,
            name='Email Candidate', email='emailcand@example.test', contact=''
        )
        LeadConfused.objects.create(lead=email_lead, executive_id=self.manager)
        LeadField_Register.objects.create(work=self.work, name='Skills', question_id=14)

        from django.core import mail
        mail.outbox.clear()
        res = self.csrf_post(f'/api/leads/{email_lead.pk}/send-interview/')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data['channel'], 'email')
        self.assertIn('e***@example.test', data['message'])
        self.assertEqual(len(mail.outbox), 1)

    def test_send_both_goes_by_email_by_default(self):
        both_lead = Leads.objects.create(
            work=self.work, collected_by=self.manager, lead_category=self.category,
            name='Both Candidate', email='both@example.test', contact='9876543210'
        )
        LeadConfused.objects.create(lead=both_lead, executive_id=self.manager)
        LeadField_Register.objects.create(work=self.work, name='Skills', question_id=14)

        from django.core import mail
        mail.outbox.clear()
        res = self.csrf_post(f'/api/leads/{both_lead.pk}/send-interview/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['channel'], 'email')

    def test_send_unnormalisable_phone_refused(self):
        bad_phone_lead = Leads.objects.create(
            work=self.work, collected_by=self.manager, lead_category=self.category,
            name='Bad Phone', email='', contact='12345'
        )
        # Bypass model clean for the test setup
        LeadConfused.objects.filter(lead=bad_phone_lead).delete()
        bad_phone_lead.contact = '123'
        Leads.objects.filter(pk=bad_phone_lead.pk).update(contact='123')
        # Add confused record directly via update
        LeadConfused.objects.create(lead=self.lead, executive_id=self.manager)

    # --- 5. COURSE REMOVED AND LEAD SOURCE OPTIONAL TESTS ---
    def test_course_removed_and_lead_source_saved_on_manual_add_and_excel(self):
        client = Client()
        from .models import LeadCateogry_TeamAllocate
        alloc = LeadCateogry_TeamAllocate.objects.create(lead_category=self.category)
        session = client.session
        session['tid'] = self.login.log_username
        session.save()

        # 1. add_lead_manual view does NOT require course; saves optional lead_source to lead.source
        res1 = client.post('/add-lead/', {
            'team_alloc_id': alloc.id,
            'name': 'Test TL Lead Source',
            'email': 'testtl_src@test.com',
            'contact_number': '9876543299',
            'lead_source': 'Walk-in',
        })
        self.assertEqual(res1.status_code, 200)
        self.assertTrue(res1.json()['success'])
        created_tl_lead = Leads.objects.get(email='testtl_src@test.com')
        self.assertEqual(created_tl_lead.source, 'Walk-in')
        self.assertFalse(LeadDetails.objects.filter(lead=created_tl_lead, field_name='Course').exists())

        # 2. lead_list view does NOT require course; saves optional lead_source to lead.source
        exec_login = LogRegister_Details.objects.create(log_username='exec_source', position='Executive')
        EmployeeRegister_Details.objects.create(login=exec_login, company=self.company, name='Exec Source')
        session['eid'] = exec_login.log_username
        session.save()
        res2 = client.post(f'/lead-list/{self.category.pk}/', {
            'full_name': 'Test Executive Source',
            'email': 'testexec_src@test.com',
            'contact': '9876543211',
            'lead_source': 'Referral',
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(res2.status_code, 200)
        self.assertTrue(res2.json()['success'])
        created_exec_lead = Leads.objects.get(email='testexec_src@test.com')
        self.assertEqual(created_exec_lead.source, 'Referral')
        self.assertFalse(LeadDetails.objects.filter(lead=created_exec_lead, field_name='Course').exists())

        # 3. Excel upload without Course column succeeds and does not error
        from django.core.files.uploadedfile import SimpleUploadedFile
        import pandas as pd
        from .views import process_excel_upload
        from django.test import RequestFactory

        df = pd.DataFrame([{
            'Name': 'Upload Candidate',
            'Email': 'up_new@test.com',
            'Contact Number': '9876543212',
            'Lead Source': 'Job Portal',
        }])
        excel_io = io.BytesIO()
        df.to_excel(excel_io, index=False)
        excel_io.seek(0)
        excel_file = SimpleUploadedFile("test_leads.xlsx", excel_io.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        factory = RequestFactory()
        req = factory.post('/upload-leads-excel/', {'excel_file': excel_file})
        req.FILES['excel_file'] = excel_file
        result = process_excel_upload(req, alloc.id, self.manager)
        self.assertTrue(result.get('success'))
        self.assertEqual(result.get('created_count'), 1)
        up_lead = Leads.objects.get(email='up_new@test.com')
        self.assertEqual(up_lead.source, 'Job Portal')

        # 4. Older Excel file with legacy 'Course' column uploads successfully, ignores Course, and adds notice
        df_legacy = pd.DataFrame([{
            'Name': 'Legacy Candidate',
            'Email': 'legacy@test.com',
            'Contact Number': '9876543213',
            'Course': 'BCA',
            'Lead Source': 'Newspaper',
        }])
        legacy_io = io.BytesIO()
        df_legacy.to_excel(legacy_io, index=False)
        legacy_io.seek(0)
        legacy_file = SimpleUploadedFile("legacy_leads.xlsx", legacy_io.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        req_legacy = factory.post('/upload-leads-excel/', {'excel_file': legacy_file})
        req_legacy.FILES['excel_file'] = legacy_file
        result_legacy = process_excel_upload(req_legacy, alloc.id, self.manager)
        self.assertTrue(result_legacy.get('success'))
        self.assertEqual(result_legacy.get('created_count'), 1)
        self.assertTrue(any('Course' in note for note in result_legacy.get('notices', [])))
        legacy_lead = Leads.objects.get(email='legacy@test.com')
        self.assertEqual(legacy_lead.source, 'Newspaper')
        self.assertFalse(LeadDetails.objects.filter(lead=legacy_lead, field_name='Course').exists())


@override_settings(
    AI_HR_API_KEY='test-api-key',
    AI_HR_URL='https://interviews.example.test/',
    INTERVIEW_LINK='https://interviews.example.test/',
    INTERVIEW_LINK_SIGN=True,
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    DEFAULT_FROM_EMAIL='hr@example.test',
    SMS_BACKEND='locmem',
)
class TestNewInterviewQuestions19To24(TestCase):
    def setUp(self):
        LocmemSMSBackend.reset()
        self.company = BusinessRegister_Details.objects.create(company_code='TEST024', company_name='Test Co 24')
        self.client_record = ClientRegister.objects.create(company=self.company, client_name='Client 24')
        self.work = WorkRegister.objects.create(company=self.company, client=self.client_record)
        self.category = LeadCategory_Register.objects.create(collection_for='Hiring')
        self.login = LogRegister_Details.objects.create(log_username='mgr24', position='Data_Manager')
        self.manager = EmployeeRegister_Details.objects.create(login=self.login, company=self.company, name='Manager 24')
        self.lead = Leads.objects.create(
            work=self.work, collected_by=self.manager, lead_category=self.category,
            name='Jane Candidate', email='jane@example.test', contact='9876543210',
            source='Campus Drive',
        )
        LeadDetails.objects.create(lead=self.lead, field_name='Course', field_data='B.Sc CS')
        LeadConfused.objects.create(lead=self.lead, executive_id=self.manager)

        self.token = make_interview_token(self.lead.pk)
        self.headers = {'HTTP_X_API_KEY': 'test-api-key', 'HTTP_X_INTERVIEW_TOKEN': self.token}
        self.client = Client()

    def request(self, path, method='get', data=None, headers=None):
        return getattr(self.client, method)(path, data=data, content_type='application/json', **(headers or self.headers))

    def test_new_question_ids_in_admin_choices_and_constraints(self):
        from .interview_questions import INTERVIEW_QUESTIONS, QUESTION_CHOICES, MIN_QUESTION_ID, MAX_QUESTION_ID
        self.assertEqual(len(INTERVIEW_QUESTIONS), 24)
        self.assertEqual(MIN_QUESTION_ID, 1)
        self.assertEqual(MAX_QUESTION_ID, 24)

        # Dropdowns list 20 mappable "id - label" choices, excluding 1, 2, 3, 19
        choices_dict = dict(QUESTION_CHOICES)
        self.assertEqual(len(choices_dict), 20)
        self.assertNotIn(1, choices_dict)
        self.assertNotIn(2, choices_dict)
        self.assertNotIn(3, choices_dict)
        self.assertNotIn(19, choices_dict)

        self.assertIn(20, choices_dict)
        self.assertEqual(choices_dict[20], '20 - Which city or town are you currently living in?')
        self.assertIn(21, choices_dict)
        self.assertEqual(choices_dict[21], '21 - Have you completed any internship so far?')
        self.assertIn(22, choices_dict)
        self.assertEqual(choices_dict[22], '22 - When did your internship start? Month and year.')
        self.assertIn(23, choices_dict)
        self.assertEqual(choices_dict[23], "23 - When did it end? Or tell us if it's still going on.")
        self.assertIn(24, choices_dict)
        self.assertEqual(choices_dict[24], '24 - What was the internship about and what work did you do?')

        # Model validation allows 24, rejects 25 and 0
        field24 = LeadField_Register(work=self.work, name='Internship Topic', question_id=24)
        field24.full_clean()
        field24.save()
        self.assertEqual(field24.question_id, 24)

        field25 = LeadField_Register(work=self.work, name='Invalid 25', question_id=25)
        with self.assertRaises(ValidationError):
            field25.full_clean()

        field0 = LeadField_Register(work=self.work, name='Invalid 0', question_id=0)
        with self.assertRaises(ValidationError):
            field0.full_clean()

    def test_cannot_map_default_questions_1_2_3_19(self):
        # 1. Model clean rejects mapping 1, 2, 3, 19
        for qid in (1, 2, 3, 19):
            field = LeadField_Register(work=self.work, name=f'Field {qid}', question_id=qid)
            with self.assertRaises(ValidationError) as ctx:
                field.full_clean()
            self.assertIn('mapped by default', str(ctx.exception))

        # 2. Views reject mapping 1, 2, 3, 19
        client = Client()

        res_add = client.post('/add-field/', {
            'category_id': self.category.id,
            'field_name': 'My Source',
            'question_id': '19',
        })
        self.assertEqual(res_add.status_code, 400)
        self.assertIn('mapped by default', res_add.json()['message'])

        valid_field = LeadField_Register.objects.create(work=self.work, name='Valid Field', question_id=20)
        res_edit = client.post('/edit-field/', {
            'field_id': valid_field.id,
            'field_name': 'Updated Field',
            'question_id': '1',
        })
        self.assertEqual(res_edit.status_code, 400)
        self.assertIn('mapped by default', res_edit.json()['message'])

    def test_clear_default_mapped_fields_command(self):
        # Create a field directly with question_id=19 bypassing clean()
        f_default = LeadField_Register.objects.create(work=self.work, name='Direct Source', question_id=19)

        # Dry run does not clear
        out = io.StringIO()
        call_command('clear_default_mapped_fields', stdout=out)
        self.assertIn('DRY RUN', out.getvalue())
        f_default.refresh_from_db()
        self.assertEqual(f_default.question_id, 19)

        # --apply clears question_id to None
        out_apply = io.StringIO()
        call_command('clear_default_mapped_fields', apply=True, stdout=out_apply)
        self.assertIn('Successfully cleared question_id on 1 field(s)', out_apply.getvalue())
        f_default.refresh_from_db()
        self.assertIsNone(f_default.question_id)

    def test_lead_source_19_asked_only_when_source_is_empty(self):
        # 1. Source is filled -> 19 is not asked
        self.lead.source = 'Website'
        self.lead.save()
        q = get_lead_missing_interview_questions(self.lead)
        qids = [item['question_id'] for item in q]
        self.assertNotIn(19, qids)

        # 2. Source is empty -> 19 is asked
        self.lead.source = ''
        self.lead.save()
        q = get_lead_missing_interview_questions(self.lead)
        qids = [item['question_id'] for item in q]
        self.assertIn(19, qids)

        # 3. Source is pure whitespace -> 19 is asked
        self.lead.source = '   '
        self.lead.save()
        q = get_lead_missing_interview_questions(self.lead)
        qids = [item['question_id'] for item in q]
        self.assertIn(19, qids)

    def test_custom_questions_20_to_24_asked_only_when_mapped_and_empty(self):
        # When not mapped, 20-24 are not asked
        q = get_lead_missing_interview_questions(self.lead)
        qids = [item['question_id'] for item in q]
        for qid in (20, 21, 22, 23, 24):
            self.assertNotIn(qid, qids)

        # Map 20 (Location) to work -> now asked
        loc_field = LeadField_Register.objects.create(work=self.work, name='Location', question_id=20)
        q = get_lead_missing_interview_questions(self.lead)
        qids = [item['question_id'] for item in q]
        self.assertIn(20, qids)

        # Fill Location in LeadDetails -> no longer asked
        LeadDetails.objects.create(lead=self.lead, field_name='Location', field_data='Kochi')
        q = get_lead_missing_interview_questions(self.lead)
        qids = [item['question_id'] for item in q]
        self.assertNotIn(20, qids)

    def test_internship_dependency_rules(self):
        # Map 21, 22, 23, 24
        f21 = LeadField_Register.objects.create(work=self.work, name='Internship Done', question_id=21)
        f22 = LeadField_Register.objects.create(work=self.work, name='Internship Start', question_id=22)
        f23 = LeadField_Register.objects.create(work=self.work, name='Internship End', question_id=23)
        f24 = LeadField_Register.objects.create(work=self.work, name='Internship Topic', question_id=24)

        # Case A: 21 is empty -> 21, 22, 23, 24 are all asked
        q = get_lead_missing_interview_questions(self.lead)
        qids = [item['question_id'] for item in q]
        self.assertEqual(qids, [21, 22, 23, 24])

        # Case B: 21 is "Yes" -> 21 is omitted, 22, 23, 24 are asked
        detail_21 = LeadDetails.objects.create(lead=self.lead, field_name='Internship Done', field_data='Yes')
        q = get_lead_missing_interview_questions(self.lead)
        qids = [item['question_id'] for item in q]
        self.assertEqual(qids, [22, 23, 24])

        # Case C: 21 is "No" (case-insensitive) -> 21 is omitted, AND 22, 23, 24 are suppressed!
        detail_21.field_data = 'No'
        detail_21.save()
        q = get_lead_missing_interview_questions(self.lead)
        qids = [item['question_id'] for item in q]
        self.assertEqual(qids, [])

        # Case D: Canonical 'no' in lowercase
        detail_21.field_data = 'no'
        detail_21.save()
        q = get_lead_missing_interview_questions(self.lead)
        self.assertEqual([item['question_id'] for item in q], [])

    def test_answers_19_to_24_saved_and_source_copied_only_when_empty(self):
        # Map 20 (Location) and 21 (Internship Done)
        LeadField_Register.objects.create(work=self.work, name='Current Location', question_id=20)
        LeadField_Register.objects.create(work=self.work, name='Any Internship', question_id=21)

        # Clear lead.source first
        self.lead.source = ''
        self.lead.save()

        # 1. Answer question 19
        res19 = self.request('/api/interview/answer/', 'post', {
            'token': self.token,
            'question_id': 19,
            'answer': 'Social Media',
        })
        self.assertEqual(res19.status_code, 200)
        self.assertTrue(res19.json()['success'])
        self.lead.refresh_from_db()
        self.assertEqual(self.lead.source, 'Social Media')
        self.assertTrue(LeadDetails.objects.filter(lead=self.lead, field_name='Lead Source', field_data='Social Media').exists())

        # 2. Resend question 19 with different answer when source is already populated
        res19_resend = self.request('/api/interview/answer/', 'post', {
            'token': self.token,
            'question_id': 19,
            'answer': 'Friend/Referral',
        })
        self.assertEqual(res19_resend.status_code, 200)
        self.lead.refresh_from_db()
        # Does NOT overwrite existing column value
        self.assertEqual(self.lead.source, 'Social Media')
        # Overwrites LeadDetails
        self.assertTrue(LeadDetails.objects.filter(lead=self.lead, field_name='Lead Source', field_data='Friend/Referral').exists())

        # 3. Answer question 20 (Location) and 21 (Internship Done)
        res20 = self.request('/api/interview/answer/', 'post', {
            'token': self.token,
            'question_id': 20,
            'answer': 'Trivandrum',
        })
        self.assertEqual(res20.status_code, 200)
        self.assertTrue(LeadDetails.objects.filter(lead=self.lead, field_name='Current Location', field_data='Trivandrum').exists())

        res21 = self.request('/api/interview/answer/', 'post', {
            'token': self.token,
            'question_id': 21,
            'answer': 'Yes',
        })
        self.assertEqual(res21.status_code, 200)
        self.assertTrue(LeadDetails.objects.filter(lead=self.lead, field_name='Any Internship', field_data='Yes').exists())

        # 4. Resend question 20 overwrites without duplicates
        res20_resend = self.request('/api/interview/answer/', 'post', {
            'token': self.token,
            'question_id': 20,
            'answer': 'Bengaluru',
        })
        self.assertEqual(res20_resend.status_code, 200)
        self.assertEqual(LeadDetails.objects.filter(lead=self.lead, field_name='Current Location').count(), 1)
        self.assertEqual(LeadDetails.objects.get(lead=self.lead, field_name='Current Location').field_data, 'Bengaluru')

    def test_unknown_question_id_25_gives_400(self):
        res = self.request('/api/interview/answer/', 'post', {
            'token': self.token,
            'question_id': 25,
            'answer': 'Invalid Question',
        })
        self.assertEqual(res.status_code, 400)
        self.assertIn('Unknown question id: 25', res.json()['error'])

    def test_walk_lead_with_only_location_and_internship_done_no_missing(self):
        """
        Walk a lead where:
          - Default fields (Name, Email, Phone, Course, Source) are all filled.
          - Work maps Location (20), Internship Done (21), Start (22), End (23), Topic (24).
          - Lead already has internship_done = "No".
          - Only Location (20) is missing.
          - Verification: Session endpoint returns exactly [20].
        """
        LeadField_Register.objects.create(work=self.work, name='Location', question_id=20)
        LeadField_Register.objects.create(work=self.work, name='Internship Done', question_id=21)
        LeadField_Register.objects.create(work=self.work, name='Internship Start', question_id=22)
        LeadField_Register.objects.create(work=self.work, name='Internship End', question_id=23)
        LeadField_Register.objects.create(work=self.work, name='Internship Topic', question_id=24)

        # Set internship_done = "No" in LeadDetails
        LeadDetails.objects.create(lead=self.lead, field_name='Internship Done', field_data='No')

        # Call session endpoint via GET /api/interview/session/
        res = self.request('/api/interview/session/')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        questions = data['questions']
        qids = [q['question_id'] for q in questions]

        # Location (20) is asked; 21 is filled; 22, 23, 24 are suppressed by "No"
        self.assertEqual(qids, [20])
        self.assertEqual(questions[0]['field_key'], 'location')


@override_settings(
    AI_HR_API_KEY='test-api-key',
    AI_HR_URL='https://interviews.example.test/',
    INTERVIEW_LINK='https://interviews.example.test/',
    INTERVIEW_LINK_SIGN=True,
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    DEFAULT_FROM_EMAIL='career@altostechnologies.in',
    COMPANY_NAME='Altos Technologies',
    SMS_BACKEND='locmem',
)
class InterviewInvitationEmailTests(TestCase):
    def setUp(self):
        LocmemSMSBackend.reset()
        self.company = BusinessRegister_Details.objects.create(company_code='INV001', company_name='Inv Co')
        self.login = LogRegister_Details.objects.create(log_username='inv_mgr', position='Data_Manager')
        self.manager = EmployeeRegister_Details.objects.create(login=self.login, company=self.company, name='Inv Manager')
        self.work = WorkRegister.objects.create(company=self.company)
        self.client_task = ClientTask_Register.objects.create(company=self.company, work=self.work, task_name='Inv Task')
        self.category = LeadCategory_Register.objects.create(client_task=self.client_task, collection_for='Inv Hiring')
        self.lead = Leads.objects.create(
            collected_by=self.manager, work=self.work, lead_category=self.category,
            name='Jane Candidate', email='jane@example.test', contact='9876543211',
        )
        LeadConfused.objects.create(lead=self.lead, executive_id=self.manager)
        LeadField_Register.objects.create(
            work=self.work, lead_category=self.category,
            name='Experience', description='Describe experience', question_id=5
        )
        self.path = f'/api/leads/{self.lead.pk}/send-interview/'
        self.client = Client(enforce_csrf_checks=True)
        session = self.client.session
        session['did'] = 'inv_mgr'
        session.save()

    def csrf_post(self, path):
        self.client.get('/databank/')
        token = self.client.cookies['csrftoken'].value
        return self.client.post(path, HTTP_X_CSRFTOKEN=token)

    def test_interview_invitation_email_details_in_outbox(self):
        from django.core import mail
        mail.outbox.clear()

        response = self.csrf_post(self.path)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)

        msg = mail.outbox[0]
        company_name = getattr(settings, 'COMPANY_NAME', 'Altos Technologies')

        # 1. Subject
        self.assertEqual(msg.subject, f"Your interview invitation from {company_name}")

        # 2. From & To & Reply-To
        self.assertEqual(msg.from_email, settings.DEFAULT_FROM_EMAIL)
        self.assertEqual(msg.to, ['jane@example.test'])
        self.assertEqual(msg.reply_to, [settings.DEFAULT_FROM_EMAIL])

        # 3. Multipart: both text and HTML present
        self.assertTrue(msg.body)
        self.assertEqual(len(msg.alternatives), 1)
        html_content, mimetype = msg.alternatives[0]
        self.assertEqual(mimetype, 'text/html')

        # 4. Candidate name and link in both parts
        self.assertIn('Jane Candidate', msg.body)
        self.assertIn('Jane Candidate', html_content)
        self.assertIn('?token=', msg.body)
        self.assertIn('?token=', html_content)

        # 5. "valid for 7 days" in both parts
        self.assertIn('valid for 7 days', msg.body.lower())
        self.assertIn('valid for 7 days', html_content.lower())

        # 6. No password or secret in output
        pw = settings.EMAIL_HOST_PASSWORD or ''
        if pw:
            self.assertNotIn(pw, msg.body)
            self.assertNotIn(pw, html_content)
            self.assertNotIn(pw, msg.subject)

    def test_smtp_auth_error_returns_actionable_message(self):
        with patch('django.core.mail.EmailMultiAlternatives.send', side_effect=smtplib.SMTPAuthenticationError(535, b'BadCredentials')):
            response = self.csrf_post(self.path)
        self.assertEqual(response.status_code, 502)
        self.assertIn('Mail login failed', response.json()['message'])

    def test_smtp_server_disconnected_returns_actionable_message(self):
        with patch('django.core.mail.EmailMultiAlternatives.send', side_effect=smtplib.SMTPServerDisconnected('Connection unexpectedly closed')):
            response = self.csrf_post(self.path)
        self.assertEqual(response.status_code, 502)
        self.assertIn('SMTP server disconnected unexpectedly', response.json()['message'])

    def test_smtp_timeout_returns_actionable_message(self):
        with patch('django.core.mail.EmailMultiAlternatives.send', side_effect=TimeoutError('timed out')):
            response = self.csrf_post(self.path)
        self.assertEqual(response.status_code, 502)
        self.assertIn('Connection to the mail server timed out', response.json()['message'])

    def test_send_test_email_management_command(self):
        from django.core.management import call_command
        from django.core import mail
        import io
        mail.outbox.clear()
        out = io.StringIO()
        call_command('send_test_email', 'testcmd@example.test', stdout=out)
        self.assertIn('Successfully sent test email', out.getvalue())
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['testcmd@example.test'])
