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
from .utils import INTERVIEW_TOKEN_MAX_AGE, make_interview_link, make_interview_token


@override_settings(AI_HR_API_KEY='test-api-key', AI_HR_URL='https://interviews.example.test/',
                   INTERVIEW_LINK='https://interviews.example.test/',
                   INTERVIEW_LINK_SIGN=True,
                   EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend', DEFAULT_FROM_EMAIL='hr@example.test')
class InterviewAPITests(TestCase):
    def setUp(self):
        self.company = BusinessRegister_Details.objects.create(company_code='TEST001', company_name='Test Co')
        self.client_record = ClientRegister.objects.create(company=self.company, client_name='Client')
        self.work = WorkRegister.objects.create(company=self.company, client=self.client_record)
        self.category = LeadCategory_Register.objects.create(collection_for='Hiring')
        self.login = LogRegister_Details.objects.create(log_username='manager', position='Data_Manager')
        self.manager = EmployeeRegister_Details.objects.create(login=self.login, company=self.company, name='Manager')
        self.lead = Leads.objects.create(work=self.work, collected_by=self.manager, lead_category=self.category,
                                         name='Candidate One', email='candidate@example.test')
        self.field = LeadField_Register.objects.create(work=self.work, lead_category=self.category,
                                                       name='Experience', description='Describe your experience', question_id=4)
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
        )
        token = make_interview_token(lead.pk)
        with self.assertLogs('digitalmarketing.views', level='WARNING') as logs:
            response = self.request('/api/interview/session/', headers={
                'HTTP_X_API_KEY': 'test-api-key', 'HTTP_X_INTERVIEW_TOKEN': token,
            })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['questions'], [])
        self.assertIn(f'lead_id={lead.pk}', logs.output[0])

    def test_question_id_is_unique_per_work_and_validated(self):
        from django.core.exceptions import ValidationError

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
            'question_id': '19',
        })
        self.assertEqual(invalid.status_code, 400)
        self.assertIn('valid interview question', invalid.json()['message'])

    def test_token_errors_and_unknown_lead(self):
        for token, status in (('', 400), ('tampered', 400)):
            headers = {'HTTP_X_API_KEY': 'test-api-key', 'HTTP_X_INTERVIEW_TOKEN': token}
            self.assertEqual(self.request('/api/interview/session/', headers=headers).status_code, status)
        expired = signing.dumps({'lead': self.lead.pk}, salt='interview-link')
        with patch('django.core.signing.time.time', return_value=timezone.now().timestamp() + 8 * 24 * 60 * 60):
            response = self.request('/api/interview/session/', headers={
                'HTTP_X_API_KEY': 'test-api-key', 'HTTP_X_INTERVIEW_TOKEN': expired,
            })
        self.assertEqual(response.status_code, 410)
        unknown = signing.dumps({'lead': 999999}, salt='interview-link')
        response = self.request('/api/interview/session/', headers={
            'HTTP_X_API_KEY': 'test-api-key', 'HTTP_X_INTERVIEW_TOKEN': unknown,
        })
        self.assertEqual(response.status_code, 404)

    def test_token_errors_are_shared_by_each_endpoint(self):
        expired = signing.dumps({'lead': self.lead.pk}, salt='interview-link')
        with patch('django.core.signing.time.time', return_value=timezone.now().timestamp() + 8 * 24 * 60 * 60):
            expired_token = expired
            for path, method, data in (
                ('/api/interview/session/', 'get', None),
                ('/api/interview/answer/', 'post', {'answers': [{'question_id': 4, 'answer': 'Answer'}]}),
                ('/api/interview/complete/', 'post', {}),
            ):
                headers = {'HTTP_X_API_KEY': 'test-api-key', 'HTTP_X_INTERVIEW_TOKEN': expired_token}
                self.assertEqual(self.request(path, method, data, headers).status_code, 410)
        for token, status in (('tampered', 400), ('', 400),
                              (signing.dumps({'lead': 999999}, salt='interview-link'), 404)):
            for path, method, data in (
                ('/api/interview/session/', 'get', None),
                ('/api/interview/answer/', 'post', {'answers': [{'question_id': 4, 'answer': 'Answer'}]}),
                ('/api/interview/complete/', 'post', {}),
            ):
                headers = {'HTTP_X_API_KEY': 'test-api-key', 'HTTP_X_INTERVIEW_TOKEN': token}
                self.assertEqual(self.request(path, method, data, headers).status_code, status)

    def test_answer_validation_truncation_and_update(self):
        bad_field = self.request('/api/interview/answer/', 'post', {
            'token': self.token, 'answers': [{'question_id': 15, 'answer': 'Answer'}],
        })
        self.assertEqual(bad_field.status_code, 400)
        long_answer = 'a' * 900
        response = self.request('/api/interview/answer/', 'post', {
            'token': self.token, 'answers': [{'question_id': 4, 'answer': long_answer}],
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(LeadDetails.objects.get(lead=self.lead, field_name='Experience').field_data, 'a' * 855)
        self.request('/api/interview/answer/', 'post', {
            'token': self.token, 'answers': [{'question_id': 4, 'answer': 'Updated'}],
        })
        self.assertEqual(LeadDetails.objects.filter(lead=self.lead, field_name='Experience').count(), 1)
        self.assertEqual(LeadDetails.objects.get(lead=self.lead, field_name='Experience').field_data, 'Updated')
        self.assertEqual(self.request('/api/interview/answer/', 'post', {
            'token': self.token, 'answers': [{'question_id': 4, 'answer': '  '}],
        }).status_code, 400)

    def test_answer_endpoint_rejects_unknown_question_and_bad_body_token(self):
        unknown = self.request('/api/interview/answer/', 'post', {
            'token': self.token, 'answers': [{'question_id': 99, 'answer': 'Answer'}],
        })
        self.assertEqual(unknown.status_code, 400)
        self.assertIn('Unknown question id: 99', unknown.json()['error'])

        bad_token = self.request('/api/interview/answer/', 'post', {
            'token': 'tampered', 'answers': [],
        })
        self.assertEqual(bad_token.status_code, 400)

    def test_answer_and_complete_api_key_errors(self):
        for path, method, data in (
            ('/api/interview/answer/', 'post', {'answers': [{'question_id': 4, 'answer': 'Answer'}]}),
            ('/api/interview/complete/', 'post', {}),
        ):
            for headers in ({'HTTP_X_INTERVIEW_TOKEN': self.token},
                            {'HTTP_X_API_KEY': 'wrong', 'HTTP_X_INTERVIEW_TOKEN': self.token}):
                self.assertEqual(self.request(path, method, data, headers).status_code, 401)

    @override_settings(AI_HR_API_KEY='')
    def test_empty_server_api_key_denies_requests(self):
        self.assertEqual(self.request('/api/interview/session/').status_code, 401)

    def test_complete_and_completed_interview_conflicts(self):
        response = self.request('/api/interview/complete/', 'post', {})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(LeadDetails.objects.filter(lead=self.lead, field_name='AI Interview Status', field_data='Completed').exists())
        for path, method, data in (
            ('/api/interview/session/', 'get', None),
            ('/api/interview/answer/', 'post', {'token': self.token, 'answers': [{'question_id': 4, 'answer': 'Answer'}]}),
        ):
            self.assertEqual(self.request(path, method, data).status_code, 409)
        self.assertEqual(self.request('/api/interview/complete/', 'post', {}).status_code, 200)


@override_settings(AI_HR_API_KEY='test-api-key', AI_HR_URL='https://interviews.example.test/',
                   INTERVIEW_LINK='https://interviews.example.test/',
                   INTERVIEW_LINK_SIGN=True,
                   EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend', DEFAULT_FROM_EMAIL='hr@example.test')
class SendInterviewTests(TestCase):
    def setUp(self):
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
            name='Candidate One', email='candidate@example.test'
        )
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

    def test_not_confused_invalid_email_and_success_with_signed_payload_link(self):
        self.lead.email = ''
        self.lead.save()
        self.assertEqual(self.csrf_post(self.path).status_code, 400)
        self.lead.email = 'candidate@example.test'
        self.lead.save()
        self.assertEqual(self.csrf_post(self.path).status_code, 400)
        LeadConfused.objects.create(lead=self.lead, executive_id=self.manager)
        self.lead.name = '<Candidate & Ω>'
        self.lead.email = 'invalid'
        self.lead.save()
        self.assertEqual(self.csrf_post(self.path).status_code, 400)
        self.lead.email = 'candidate@example.test'
        self.lead.save()
        LeadField_Register.objects.create(work=self.work, lead_category=self.category, name='அனுபவம்', description='முன் அனுபவத்தை விவரிக்கவும்', question_id=14)
        LeadField_Register.objects.create(work=self.work, lead_category=self.category, name='Whitespace', description='   ')
        LeadField_Register.objects.create(work=self.work, lead_category=self.category, name='Trimmed', description='  trimmed description  ', question_id=15)
        response = self.csrf_post(self.path)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], 'Email sent to candidate@example.test')
        from django.core import mail
        self.assertEqual(len(mail.outbox), 1)
        message = mail.outbox[0]
        self.assertEqual(message.to, ['candidate@example.test'])
        self.assertEqual(message.subject, 'Interview Invitation')
        link = message.body.splitlines()[-1]
        self.assertEqual(message.body, f'Hello <Candidate & Ω>,\n\nConduct your interview by clicking the link below:\n{link}')
        query = parse_qs(urlsplit(link).query)
        encoded = query['data'][0]
        decoded = base64.urlsafe_b64decode(encoded + '=' * (-len(encoded) % 4)).decode('utf-8')
        expected = {
            'candidate': {'name': '<Candidate & Ω>'},
            'questions': [
                {'question_id': 4, 'field_key': 'role_applied'},
                {'question_id': 14, 'field_key': 'skills'},
                {'question_id': 15, 'field_key': 'notice_period'},
            ],
        }
        self.assertEqual(json.loads(decoded), expected)
        self.assertTrue(query['token'][0])
        self.assertEqual(json.loads(decoded).keys(), expected.keys())
        expiration = query['exp'][0]
        expected_signature = hmac.new(
            b'test-api-key', f'{encoded}.{expiration}'.encode('utf-8'), hashlib.sha256
        ).hexdigest()
        self.assertEqual(query['sig'][0], expected_signature)
        tampered = ('A' if encoded[0] != 'A' else 'B') + encoded[1:]
        tampered_signature = hmac.new(
            b'test-api-key', f'{tampered}.{expiration}'.encode('utf-8'), hashlib.sha256
        ).hexdigest()
        self.assertNotEqual(query['sig'][0], tampered_signature)
        now_timestamp = int(timezone.now().timestamp())
        self.assertGreaterEqual(int(expiration), now_timestamp + INTERVIEW_TOKEN_MAX_AGE - 2)
        self.assertLessEqual(int(expiration), now_timestamp + INTERVIEW_TOKEN_MAX_AGE)
        self.assertEqual(len(message.alternatives), 1)
        html_body, mime_type = message.alternatives[0]
        self.assertEqual(mime_type, 'text/html')
        self.assertIn('Hello &lt;Candidate &amp; Ω&gt;,', html_body)
        self.assertIn(f'href="{link.replace("&", "&amp;")}"', html_body)
        self.assertIn('Conduct your interview by clicking <a ', html_body)
        self.assertIn('>this link</a>.', html_body)
        self.assertEqual(self.csrf_post(self.path).status_code, 409)

    def test_link_for_ten_typical_fields_stays_under_limit(self):
        question_ids = [2, 3, 5, 6, 7, 8, 9, 10, 11]
        for index, question_id in enumerate(question_ids, start=2):
            LeadField_Register.objects.create(
                work=self.work,
                name=f'Question {index}',
                description=f'Please provide a brief description for question {index}.',
                question_id=question_id,
            )
        link, payload = make_interview_link(self.lead)
        self.assertEqual(len(payload['questions']), 10)
        self.assertLessEqual(len(link), 1800)

    def test_signing_can_be_disabled_and_empty_key_skips_signature(self):
        with override_settings(INTERVIEW_LINK_SIGN=False):
            unsigned_link, _ = make_interview_link(self.lead)
        unsigned_query = parse_qs(urlsplit(unsigned_link).query)
        self.assertNotIn('exp', unsigned_query)
        self.assertNotIn('sig', unsigned_query)

        with override_settings(INTERVIEW_LINK_SIGN=True, AI_HR_API_KEY=''):
            with self.assertLogs('digitalmarketing.utils', level='WARNING') as warning_log:
                empty_key_link, _ = make_interview_link(self.lead)
        empty_key_query = parse_qs(urlsplit(empty_key_link).query)
        self.assertNotIn('exp', empty_key_query)
        self.assertNotIn('sig', empty_key_query)
        self.assertIn('AI_HR_API_KEY is empty', warning_log.output[0])

    def test_no_mapped_fields_blocks_sending_invitation(self):
        LeadConfused.objects.create(lead=self.lead, executive_id=self.manager)
        LeadField_Register.objects.filter(work=self.work).delete()
        LeadField_Register.objects.create(work=self.work, name='Whitespace only', description=' \t  ')
        response = self.csrf_post(self.path)
        self.assertEqual(response.status_code, 422)
        msg = response.json()['message']
        self.assertIn('no fields mapped to interview questions', msg)
        self.assertIn(f'Work #{self.work.pk}', msg)
        self.assertIn('Whitespace only', msg)
        from django.core import mail
        self.assertEqual(mail.outbox, [])

    def test_resolves_registered_work_through_lead_collection_category(self):
        from .utils import make_interview_payload
        self.lead.work = None
        self.lead.save(update_fields=['work'])
        payload = make_interview_payload(self.lead)
        self.assertEqual(payload['questions'], [
            {'question_id': 4, 'field_key': 'role_applied'},
        ])

    def test_long_field_descriptions_are_not_embedded_in_interview_link(self):
        LeadConfused.objects.create(lead=self.lead, executive_id=self.manager)
        field = LeadField_Register.objects.get(work=self.work, name='Experience')
        field.description = 'x' * 3000
        field.save(update_fields=['description'])
        link, _ = make_interview_link(self.lead)
        self.assertLessEqual(len(link), 1800)
        response = self.csrf_post(self.path)
        self.assertEqual(response.status_code, 200)
        from django.core import mail
        self.assertEqual(len(mail.outbox), 1)

    def test_leads_from_different_works_get_their_own_questions(self):
        other_work = WorkRegister.objects.create(company=self.company)
        other_lead = Leads.objects.create(
            work=other_work, collected_by=self.manager, name='Other Candidate', email='other@example.test'
        )
        LeadField_Register.objects.create(work=other_work, name='Portfolio', description='Describe your portfolio', question_id=14)
        first_link, first_payload = make_interview_link(self.lead)
        second_link, second_payload = make_interview_link(other_lead)
        self.assertNotEqual(first_link, second_link)
        self.assertEqual(first_payload['questions'], [{'question_id': 4, 'field_key': 'role_applied'}])
        self.assertEqual(second_payload['questions'], [{'question_id': 14, 'field_key': 'skills'}])

    def test_interview_link_command_prints_link_and_decoded_json_only_in_debug(self):
        output = io.StringIO()
        with override_settings(DEBUG=True):
            call_command('make_interview_link', self.lead.pk, stdout=output)
        lines = output.getvalue().splitlines()
        self.assertTrue(lines[0].startswith('https://interviews.example.test/?data='))
        self.assertEqual(json.loads('\n'.join(lines[1:])), {
            'candidate': {'name': 'Candidate One'},
            'questions': [{'question_id': 4, 'field_key': 'role_applied'}],
        })
        with override_settings(DEBUG=False):
            with self.assertRaises(CommandError):
                call_command('make_interview_link', self.lead.pk, stdout=io.StringIO())

    def test_smtp_dns_failure_returns_actionable_error(self):
        LeadConfused.objects.create(lead=self.lead, executive_id=self.manager)
        with patch('django.core.mail.EmailMultiAlternatives.send', side_effect=socket.gaierror('getaddrinfo failed')):
            response = self.csrf_post(self.path)
        self.assertEqual(response.status_code, 502)
        self.assertIn('Could not resolve the Gmail SMTP server', response.json()['message'])
        self.assertFalse(LeadDetails.objects.filter(lead=self.lead, field_name='Interview Link Sent').exists())

    def test_smtp_login_disconnect_returns_authentication_error(self):
        LeadConfused.objects.create(lead=self.lead, executive_id=self.manager)
        with patch('django.core.mail.EmailMultiAlternatives.send', side_effect=smtplib.SMTPServerDisconnected('disconnected')):
            response = self.csrf_post(self.path)
        self.assertEqual(response.status_code, 502)
        self.assertIn('closed the SMTP session during login', response.json()['message'])


class TaskAssignStringTests(TestCase):
    def test_task_assign_string_is_null_safe(self):
        task = TaskAssign.objects.create()
        self.assertEqual(str(task), f'TaskAssign #{task.pk}')

    def test_admin_list_and_change_pages_open_for_lead_models(self):
        admin_user = get_user_model().objects.create_superuser(username='admin', email='admin@example.test', password='test')
        self.client.force_login(admin_user)
        lead = Leads.objects.create(name='Admin Lead')
        details = LeadDetails.objects.create(lead=lead, field_name='Field', field_data='Value')
        task = TaskAssign.objects.create()
        for model_name, obj in (('leads', lead), ('leaddetails', details), ('taskassign', task)):
            with self.subTest(model=model_name):
                self.assertEqual(self.client.get(f'/admin/digitalmarketing/{model_name}/').status_code, 200)
                self.assertEqual(self.client.get(f'/admin/digitalmarketing/{model_name}/{obj.pk}/change/').status_code, 200)


class DataBankLeadsAPITests(TestCase):
    def setUp(self):
        self.company = BusinessRegister_Details.objects.create(company_code='BANK001', company_name='Test Co')
        self.client_record = ClientRegister.objects.create(company=self.company, client_name='Client')
        self.login = LogRegister_Details.objects.create(log_username='manager', position='Data_Manager')
        self.manager = EmployeeRegister_Details.objects.create(login=self.login, company=self.company, name='Executive')
        self.work = WorkRegister.objects.create(company=self.company, client=self.client_record)
        self.category = LeadCategory_Register.objects.create(collection_for='Hiring')
        self.lead = Leads.objects.create(work=self.work, collected_by=self.manager,
                                         lead_category=self.category, name='Needle Candidate',
                                         email='needle@example.test')
        LeadConfused.objects.create(lead=self.lead, executive_id=self.manager)
        DataBank.objects.create(lead=self.lead, lead_status='Allocated')
        session = self.client.session
        session['did'] = 'manager'
        session.save()

    def test_existing_list_endpoint_filters_search_and_pagination(self):
        response = self.client.get('/api/leads/', {'client': self.client_record.pk, 'category': self.category.pk,
                                                   'hr': self.manager.pk, 'status': 'Allocated',
                                                   'search': 'needle', 'page_size': 1})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['count'], 1)
        self.assertEqual(data['page_size'], 1)
        self.assertTrue(data['results'][0]['is_confused'])
        self.assertEqual(data['results'][0]['executive_name'], 'Executive')
        self.assertEqual(data['results'][0]['category_name'], 'Hiring')
        self.assertEqual(self.client.get('/api/leads/', {'search': 'no-match'}).json()['count'], 0)

    def test_missing_manager_session_is_forbidden(self):
        self.client.get('/logout')
        self.client.session.flush()
        self.assertEqual(self.client.get('/api/leads/').status_code, 403)



class HardeningAndMappingTests(TestCase):
    def setUp(self):
        self.company = BusinessRegister_Details.objects.create(company_code='HARD001', company_name='Hardening Co')
        self.client_record = ClientRegister.objects.create(company=self.company, client_name='StarkTech')
        self.work = WorkRegister.objects.create(company=self.company, client=self.client_record)
        self.client_task = ClientTask_Register.objects.create(
            company=self.company, client=self.client_record, work=self.work, task_name='Lead Collection'
        )
        self.category = LeadCategory_Register.objects.create(client_task=self.client_task, collection_for='Interview')
        self.exec_login = LogRegister_Details.objects.create(log_username='exec@example.test', position='Executive')
        self.executive = EmployeeRegister_Details.objects.create(
            login=self.exec_login, company=self.company, name='Executive One'
        )
        self.dm_login = LogRegister_Details.objects.create(log_username='dm@example.test', position='Data_Manager')
        self.dm = EmployeeRegister_Details.objects.create(
            login=self.dm_login, company=self.company, name='Data Manager'
        )

    def test_map_default_fields_command_maps_client_fields(self):
        names_and_expected = [
            ('Full Name', 1),
            ('Email', 2),
            ('Contact Number', 3),
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

    def test_admin_pages_for_leadfield_work_and_client(self):
        admin_user = get_user_model().objects.create_superuser(
            username='admin2', email='admin2@example.test', password='test'
        )
        self.client.force_login(admin_user)
        field = LeadField_Register.objects.create(
            work=self.work, client=self.client_record, lead_category=self.category,
            name='Notice period', description='Notice period', question_id=15,
        )
        for model_name, obj in (
            ('leadfield_register', field),
            ('workregister', self.work),
            ('clientregister', self.client_record),
        ):
            with self.subTest(model=model_name):
                res = self.client.get(f'/admin/digitalmarketing/{model_name}/')
                self.assertEqual(res.status_code, 200)
                if model_name == 'leadfield_register':
                    self.assertContains(res, '15 - Notice period / how soon can start')
                self.assertEqual(self.client.get(f'/admin/digitalmarketing/{model_name}/{obj.pk}/change/').status_code, 200)

    @override_settings(AI_HR_API_KEY='test-api-key')
    def test_answer_endpoint_accepts_legacy_field_formats(self):
        field = LeadField_Register.objects.create(
            work=self.work, lead_category=self.category, name='skills', question_id=14
        )
        lead = Leads.objects.create(
            work=self.work, collected_by=self.executive, lead_category=self.category,
            name='Legacy Candidate', email='legacy@example.test'
        )
        token = make_interview_token(lead.pk)
        headers = {'HTTP_X_API_KEY': 'test-api-key', 'HTTP_X_INTERVIEW_TOKEN': token}

        res1 = self.client.post(
            '/api/interview/answer/',
            data=json.dumps({'token': token, 'answers': [{'field_id': field.pk, 'answer': 'Python'}]}),
            content_type='application/json',
            **headers,
        )
        self.assertEqual(res1.status_code, 200)
        self.assertEqual(LeadDetails.objects.get(lead=lead, field_name='skills').field_data, 'Python')

        res2 = self.client.post(
            '/api/interview/answer/',
            data=json.dumps({'token': token, 'answers': [{'field': 'skills', 'answer': 'Python, Django'}]}),
            content_type='application/json',
            **headers,
        )
        self.assertEqual(res2.status_code, 200)
        self.assertEqual(LeadDetails.objects.get(lead=lead, field_name='skills').field_data, 'Python, Django')

    @override_settings(INTERVIEW_LINK_SIGN=True, AI_HR_API_KEY='')
    def test_send_interview_blocks_when_api_key_missing(self):
        LeadField_Register.objects.create(
            work=self.work, lead_category=self.category, name='skills', question_id=14
        )
        lead = Leads.objects.create(
            work=self.work, collected_by=self.executive, lead_category=self.category,
            name='Keyless Candidate', email='keyless@example.test'
        )
        LeadConfused.objects.create(lead=lead, executive_id=self.executive)
        csrf_client = Client(enforce_csrf_checks=True)
        session = csrf_client.session
        session['did'] = 'dm@example.test'
        session.save()
        csrf_client.get('/databank/')
        csrf_token = csrf_client.cookies['csrftoken'].value
        res = csrf_client.post(f'/api/leads/{lead.pk}/send-interview/', HTTP_X_CSRFTOKEN=csrf_token)
        self.assertEqual(res.status_code, 503)
        self.assertIn('AI_HR_API_KEY', res.json()['message'])

    def test_executive_lead_collection_without_lead_source(self):
        LeadField_Register.objects.create(
            work=self.work, lead_category=self.category, name='Notice period', question_id=15
        )
        session = self.client.session
        session['eid'] = 'exec@example.test'
        session.save()
        res = self.client.post(
            f'/lead-list/{self.category.pk}/',
            {
                'full_name': 'Sample Candidate',
                'email': 'sample@example.test',
                'contact': '9876543210',
                'notice-period': '15 days',
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.assertEqual(res.status_code, 200)
        lead = Leads.objects.get(email='sample@example.test')
        self.assertIsNone(lead.source)
        self.assertEqual(lead.work, self.work)
        self.assertEqual(LeadDetails.objects.get(lead=lead, field_name='Notice period').field_data, '15 days')

    @override_settings(
        AI_HR_API_KEY='test-api-key',
        AI_HR_URL='https://interviews.example.test/',
        INTERVIEW_LINK='https://interviews.example.test/',
        INTERVIEW_LINK_SIGN=True,
        EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
        DEFAULT_FROM_EMAIL='hr@example.test',
    )
    def test_category_linked_fields_with_null_work_resolve_end_to_end(self):
        jishnu_client = ClientRegister.objects.create(company=self.company, client_name='Jishnu Anil')
        jishnu_work = WorkRegister.objects.create(company=self.company, client=jishnu_client)
        jishnu_task = ClientTask_Register.objects.create(
            company=self.company, client=jishnu_client, work=jishnu_work, task_name='Lead Collection'
        )
        jishnu_cat = LeadCategory_Register.objects.create(client_task=jishnu_task, collection_for='Interview')

        f_notice = LeadField_Register.objects.create(lead_category=jishnu_cat, name='Notice period')
        f_qual = LeadField_Register.objects.create(lead_category=jishnu_cat, name='Highest qualification')
        f_skills = LeadField_Register.objects.create(lead_category=jishnu_cat, name='skills')

        dm_head_login = LogRegister_Details.objects.create(log_username='head@example.test', position='Digital_Marketing_Head')
        EmployeeRegister_Details.objects.create(login=dm_head_login, company=self.company, name='DM Head')
        head_session = self.client.session
        head_session['hid'] = 'head@example.test'
        head_session.save()
        page_res = self.client.get(f'/fields/{jishnu_work.pk}/')
        self.assertEqual(page_res.status_code, 200)
        self.assertContains(page_res, 'No fields are mapped to AI interview questions yet.')
        self.assertContains(page_res, 'Notice period, Highest qualification, skills')

        lead = Leads.objects.create(
            work=None,
            lead_category=jishnu_cat,
            collected_by=self.executive,
            name='Confused Candidate',
            email='confused@example.test',
            contact='9876543211',
        )
        LeadConfused.objects.create(lead=lead, executive_id=self.executive)

        csrf_client = Client(enforce_csrf_checks=True)
        dm_session = csrf_client.session
        dm_session['did'] = 'dm@example.test'
        dm_session.save()
        csrf_client.get('/databank/')
        csrf_token = csrf_client.cookies['csrftoken'].value

        blocked = csrf_client.post(f'/api/leads/{lead.pk}/send-interview/', HTTP_X_CSRFTOKEN=csrf_token)
        self.assertEqual(blocked.status_code, 422)
        blocked_msg = blocked.json()['message']
        self.assertIn(f'Work #{jishnu_work.pk} (client: Jishnu Anil)', blocked_msg)
        self.assertIn('Notice period, Highest qualification, skills', blocked_msg)

        edit_res = self.client.post('/edit-field/', {
            'field_id': f_notice.pk,
            'field_name': 'Notice period',
            'description': 'How soon can you start?',
            'question_id': '15',
        })
        self.assertEqual(edit_res.status_code, 200)
        f_notice.refresh_from_db()
        self.assertEqual(f_notice.work_id, jishnu_work.pk)
        self.assertEqual(f_notice.question_id, 15)

        LeadField_Register.objects.filter(pk=f_qual.pk).update(question_id=5, work=None)
        LeadField_Register.objects.filter(pk=f_skills.pk).update(question_id=14, work=None)

        sent = csrf_client.post(f'/api/leads/{lead.pk}/send-interview/', HTTP_X_CSRFTOKEN=csrf_token)
        self.assertEqual(sent.status_code, 200)
        self.assertTrue(sent.json()['success'])

        token = make_interview_token(lead.pk)
        api_headers = {'HTTP_X_API_KEY': 'test-api-key', 'HTTP_X_INTERVIEW_TOKEN': token}
        sess_res = self.client.get('/api/interview/session/', **api_headers)
        self.assertEqual(sess_res.status_code, 200)
        self.assertEqual(sess_res.json()['questions'], [
            {'question_id': 5, 'field_key': 'highest_qualification'},
            {'question_id': 14, 'field_key': 'skills'},
            {'question_id': 15, 'field_key': 'notice_period'},
        ])

        ans_res = self.client.post(
            '/api/interview/answer/',
            data=json.dumps({'token': token, 'answers': [{'question_id': 14, 'answer': 'Python, Django'}]}),
            content_type='application/json',
            **api_headers,
        )
        self.assertEqual(ans_res.status_code, 200)
        self.assertEqual(LeadDetails.objects.get(lead=lead, field_name='skills').field_data, 'Python, Django')

    def test_lead_with_stale_work_uses_lead_category_work(self):
        from .utils import make_interview_payload, resolve_lead_work_id

        stale_work = WorkRegister.objects.create(company=self.company, client=self.client_record)
        LeadField_Register.objects.create(
            work=self.work, lead_category=self.category, name='Notice period', question_id=15
        )
        lead = Leads.objects.create(
            work=stale_work,
            lead_category=self.category,
            collected_by=self.executive,
            name='Mismatched Work Lead',
            email='mismatch@example.test',
        )
        self.assertEqual(resolve_lead_work_id(lead), self.work.pk)
        self.assertEqual(make_interview_payload(lead)['questions'], [
            {'question_id': 15, 'field_key': 'notice_period'},
        ])
