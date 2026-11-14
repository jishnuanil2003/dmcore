import base64
import hashlib
import hmac
import json
import logging
import time

from django.conf import settings
from django.core import signing
from django.db.models import Q

from .models import LeadField_Register
from .interview_questions import QUESTION_BY_ID


INTERVIEW_TOKEN_SALT = 'interview-link'
INTERVIEW_TOKEN_MAX_AGE = 7 * 24 * 60 * 60


def make_interview_token(lead_id):
    return signing.dumps({'lead': lead_id}, salt=INTERVIEW_TOKEN_SALT)


def read_interview_token(token):
    return signing.loads(token, salt=INTERVIEW_TOKEN_SALT, max_age=INTERVIEW_TOKEN_MAX_AGE)


def resolve_lead_work_id(lead):
    category = getattr(lead, 'lead_category', None)
    if category and category.client_task_id and category.client_task.work_id:
        return category.client_task.work_id
    if lead.work_id:
        return lead.work_id
    task_assign = getattr(lead, 'task_assign', None)
    if task_assign:
        if task_assign.client_task_id and task_assign.client_task.work_id:
            return task_assign.client_task.work_id
        if task_assign.work_assign_id and task_assign.work_assign.work_register_id:
            return task_assign.work_assign.work_register_id
    return None


def get_lead_work_fields(lead):
    work_id = resolve_lead_work_id(lead)
    if work_id:
        query = Q(work_id=work_id) | Q(
            work__isnull=True, lead_category__client_task__work_id=work_id
        )
        if lead.lead_category_id:
            query |= Q(work__isnull=True, lead_category_id=lead.lead_category_id)
        return LeadField_Register.objects.filter(query).distinct()
    if lead.lead_category_id:
        return LeadField_Register.objects.filter(
            work__isnull=True, lead_category_id=lead.lead_category_id
        ).distinct()
    return LeadField_Register.objects.none()


def make_interview_payload(lead):
    # Registered Work > Lead Collection associates fields with the work through
    # the lead category's ClientTask_Register. Resolve both work_id and any
    # category-linked fields whose work FK was left NULL.
    fields = get_lead_work_fields(lead).filter(question_id__isnull=False).order_by('question_id', 'id')
    questions = []
    seen_question_ids = set()
    for field in fields:
        if field.question_id in QUESTION_BY_ID and field.question_id not in seen_question_ids:
            seen_question_ids.add(field.question_id)
            questions.append({
                'question_id': field.question_id,
                'field_key': QUESTION_BY_ID[field.question_id][0],
            })

    return {
        'candidate': {'name': lead.name or ''},
        'questions': questions,
    }


def make_interview_link(lead, now=None):
    payload = make_interview_payload(lead)
    serialized = json.dumps(payload, separators=(',', ':'), ensure_ascii=False)
    encoded = base64.urlsafe_b64encode(serialized.encode('utf-8')).decode('ascii').rstrip('=')
    # The browser app needs the opaque lead credential for the session/answer
    # API calls. Keep it separate from the candidate payload so the payload
    # can be displayed without exposing a database ID.
    token = make_interview_token(lead.pk)
    link = f'{settings.INTERVIEW_LINK}?data={encoded}&token={token}'

    if settings.INTERVIEW_LINK_SIGN:
        if settings.AI_HR_API_KEY:
            expires_at = int(time.time() if now is None else now) + INTERVIEW_TOKEN_MAX_AGE
            signing_message = f'{encoded}.{expires_at}'.encode('utf-8')
            signature = hmac.new(
                settings.AI_HR_API_KEY.encode('utf-8'),
                signing_message,
                hashlib.sha256,
            ).hexdigest()
            link += f'&exp={expires_at}&sig={signature}'
        else:
            logging.getLogger(__name__).warning(
                'INTERVIEW_LINK_SIGN is enabled but AI_HR_API_KEY is empty; '
                'generating an unsigned interview link for lead_id=%s',
                lead.pk,
            )

    return link, payload
