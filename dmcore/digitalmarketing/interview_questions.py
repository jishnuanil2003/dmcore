"""Permanent question IDs understood by the interview video bot.

Append new IDs only. Never renumber or reuse an existing ID.
"""

INTERVIEW_QUESTIONS = [
    (1, 'full_name', 'Full name'),
    (2, 'email', 'Email address'),
    (3, 'phone', 'Phone number (country code if outside India)'),
    (4, 'role_applied', 'Role applying for'),
    (5, 'highest_qualification', 'Highest educational qualification'),
    (6, 'field_of_study', 'Field of study / specialization'),
    (7, 'college', 'College / university'),
    (8, 'graduation_year', 'Graduation year (or expected)'),
    (9, 'academic_performance', 'CGPA / percentage'),
    (10, 'has_experience', 'Prior work experience? (Yes / fresher)'),
    (11, 'last_company', 'Most recent company'),
    (12, 'last_role', 'Role / job title there'),
    (13, 'experience_duration', 'Total experience duration'),
    (14, 'skills', 'Top technical skills'),
    (15, 'notice_period', 'Notice period / how soon can start'),
    (16, 'expected_salary', 'Expected annual salary range'),
    (17, 'linkedin', 'LinkedIn profile (optional)'),
    (18, 'why_good_fit', 'Why a good fit for the role'),
    (19, 'lead_source', 'How did you first come to know about us?'),
    (20, 'location', 'Which city or town are you currently living in?'),
    (21, 'internship_done', 'Have you completed any internship so far?'),
    (22, 'internship_start_date', 'When did your internship start? Month and year.'),
    (23, 'internship_end_date', "When did it end? Or tell us if it's still going on."),
    (24, 'internship_topic', 'What was the internship about and what work did you do?'),
]

QUESTION_BY_ID = {question_id: (key, label) for question_id, key, label in INTERVIEW_QUESTIONS}
QUESTION_CHOICES = tuple((question_id, f'{question_id} - {label}') for question_id, _key, label in INTERVIEW_QUESTIONS)
MIN_QUESTION_ID = min(QUESTION_BY_ID)
MAX_QUESTION_ID = max(QUESTION_BY_ID)

LEAD_SOURCE_QUESTION_ID = 19
LOCATION_QUESTION_ID = 20
INTERNSHIP_DONE_QUESTION_ID = 21
INTERNSHIP_START_DATE_QUESTION_ID = 22
INTERNSHIP_END_DATE_QUESTION_ID = 23
INTERNSHIP_TOPIC_QUESTION_ID = 24
