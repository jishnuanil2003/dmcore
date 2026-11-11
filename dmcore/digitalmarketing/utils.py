import logging
from django.conf import settings
from django.core import signing
from django.db.models import Q

from .models import LeadField_Register, LeadDetails
from .interview_questions import (
    QUESTION_BY_ID,
    LEAD_SOURCE_QUESTION_ID,
    LOCATION_QUESTION_ID,
    INTERNSHIP_DONE_QUESTION_ID,
    INTERNSHIP_START_DATE_QUESTION_ID,
    INTERNSHIP_END_DATE_QUESTION_ID,
    INTERNSHIP_TOPIC_QUESTION_ID,
)


INTERVIEW_TOKEN_SALT = 'interview-link'
INTERVIEW_TOKEN_MAX_AGE = 7 * 24 * 60 * 60

# Default field mappings to permanent interview question IDs
COURSE_QUESTION_ID = 6
DEFAULT_FIELD_QUESTION_MAP = {
    'full_name': 1,
    'email': 2,
    'phone': 3,
    'course': COURSE_QUESTION_ID,
    'lead_source': LEAD_SOURCE_QUESTION_ID,
}


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


def get_lead_course_value(lead):
    """
    Find Course value for lead in LeadDetails.
    Matches field_name case-insensitively for 'course' or 'field of study'.
    Returns stripped string value or empty string.
    """
    if not lead or not lead.pk:
        return ""
    # Try prefetched or query
    details = getattr(lead, '_prefetched_objects_cache', {}).get('leaddetails_set')
    if details is None:
        details = LeadDetails.objects.filter(lead=lead)
    for d in details:
        fn = (d.field_name or '').strip().lower()
        if fn in ('course', 'field of study', 'field_of_study'):
            val = (d.field_data or '').strip()
            if val:
                return val
    return ""


def get_lead_custom_field_value(lead, field_name):
    """Find custom field value in LeadDetails for lead by field_name."""
    if not lead or not lead.pk or not field_name:
        return ""
    details = getattr(lead, '_prefetched_objects_cache', {}).get('leaddetails_set')
    if details is None:
        details = LeadDetails.objects.filter(lead=lead)
    target = field_name.strip().lower()
    for d in details:
        if (d.field_name or '').strip().lower() == target:
            return (d.field_data or '').strip()
    return ""


def get_lead_internship_done_value(lead, work_fields=None):
    """
    Find the lead's internship_done value from:
      1. Custom field mapped to question_id 21.
      2. LeadDetails entry with field_name matching 'internship_done' / 'done any internship' / etc.
      3. Direct attribute on lead (e.g. lead.done_any_internship).
    Returns stripped string or empty string.
    """
    if not lead or not getattr(lead, 'pk', None):
        return ""

    if work_fields:
        for field in work_fields:
            if field.question_id == INTERNSHIP_DONE_QUESTION_ID:
                val = get_lead_custom_field_value(lead, field.name)
                if val:
                    return val

    details = getattr(lead, '_prefetched_objects_cache', {}).get('leaddetails_set')
    if details is None:
        details = LeadDetails.objects.filter(lead=lead)
    target_names = {
        'internship_done', 'internship done', 'done any internship',
        'have you completed any internship so far?', 'internship',
        'interview q21 answer',
    }
    for d in details:
        fn = (d.field_name or '').strip().lower()
        if fn in target_names:
            val = (d.field_data or '').strip()
            if val:
                return val

    attr_val = getattr(lead, 'done_any_internship', None)
    if attr_val and isinstance(attr_val, str) and attr_val.strip():
        return attr_val.strip()

    return ""


def get_lead_missing_interview_questions(lead):
    """
    Compute which interview questions must be asked for this candidate.
    Asks only the questions whose value is not already filled on the lead:
      - Default fields: Full name -> 1, Email -> 2, Phone -> 3, Course -> 6, Lead Source -> 19.
        Include only when lead value is empty (blank or whitespace counts as empty).
      - Custom fields of the lead's work (LeadField_Register rows with a question_id):
        Include only when the lead has no non-empty value for that field in LeadDetails.
      - If a custom field is mapped to the same ID as a default field (e.g. custom field on 6 or 19):
        Dedupe, treat the question as needed if EITHER value is empty, and log/report the conflict.
      - Internship dependency: when the lead's internship_done value is "No" (case-insensitive),
        do not ask 22, 23 or 24 even if empty. When it is "Yes" or still empty, ask them as normal.
      - Result is ordered by question_id, each id once.
    """
    logger = logging.getLogger(__name__)

    # Default field emptiness checks
    name_empty = not bool(lead.name and lead.name.strip())
    email_empty = not bool(lead.email and lead.email.strip())
    phone_empty = not bool(lead.contact and lead.contact.strip())
    course_val = get_lead_course_value(lead)
    course_empty = not bool(course_val and course_val.strip())
    source_val = getattr(lead, 'source', None) or ""
    source_empty = not bool(source_val and source_val.strip())

    default_status = {
        1: name_empty,
        2: email_empty,
        3: phone_empty,
        COURSE_QUESTION_ID: course_empty,
        LEAD_SOURCE_QUESTION_ID: source_empty,
    }

    # Custom fields of the lead's work
    work_fields = list(get_lead_work_fields(lead).filter(question_id__isnull=False).order_by('question_id', 'id'))
    custom_needed_by_qid = {}
    custom_field_by_qid = {}

    for field in work_fields:
        qid = field.question_id
        if qid not in QUESTION_BY_ID:
            continue
        val = get_lead_custom_field_value(lead, field.name)
        is_empty = not bool(val and val.strip())
        custom_field_by_qid[qid] = field.name
        if is_empty:
            custom_needed_by_qid[qid] = True
        elif qid not in custom_needed_by_qid:
            custom_needed_by_qid[qid] = False

    # Check for conflicts where custom field is mapped to a default field ID
    needed_qids = set()
    all_qids = set(default_status.keys()).union(custom_field_by_qid.keys())

    for qid in all_qids:
        in_default = qid in default_status
        in_custom = qid in custom_field_by_qid

        if in_default and in_custom:
            c_name = custom_field_by_qid[qid]
            logger.warning(
                "Conflict detected on question_id %s for lead_id=%s: mapped to both default field and custom field '%s'. "
                "Treating question as needed if either value is empty.",
                qid, getattr(lead, 'pk', None), c_name
            )
            # Needed if either default is empty OR custom is empty
            if default_status[qid] or custom_needed_by_qid.get(qid, False):
                needed_qids.add(qid)
        elif in_default:
            if default_status[qid]:
                needed_qids.add(qid)
        elif in_custom:
            if custom_needed_by_qid.get(qid, False):
                needed_qids.add(qid)

    # Internship dependency: when the lead's internship_done value is "No" (case-insensitive),
    # do not ask 22, 23 or 24 even if empty. When it is "Yes" or still empty, ask them as normal.
    internship_done_val = get_lead_internship_done_value(lead, work_fields).strip().lower()
    if internship_done_val == 'no':
        needed_qids.discard(INTERNSHIP_START_DATE_QUESTION_ID)
        needed_qids.discard(INTERNSHIP_END_DATE_QUESTION_ID)
        needed_qids.discard(INTERNSHIP_TOPIC_QUESTION_ID)

    # Order by question_id ascending
    sorted_qids = sorted(needed_qids)
    questions = [
        {
            'question_id': qid,
            'field_key': QUESTION_BY_ID[qid][0],
        }
        for qid in sorted_qids
        if qid in QUESTION_BY_ID
    ]
    return questions


def make_interview_payload(lead):
    questions = get_lead_missing_interview_questions(lead)
    return {
        'candidate': {'name': lead.name or ''},
        'questions': questions,
    }


def make_interview_link(lead):
    """
    Construct short interview link: <INTERVIEW_LINK>?token=<signed lead token>.
    The bot reads only ?token=.
    """
    token = make_interview_token(lead.pk)
    base_url = settings.INTERVIEW_LINK
    sep = '&' if '?' in base_url else '?'
    link = f"{base_url}{sep}token={token}"
    payload = make_interview_payload(lead)
    return link, payload
