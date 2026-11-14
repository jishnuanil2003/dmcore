from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Q

from digitalmarketing.interview_questions import QUESTION_BY_ID
from digitalmarketing.models import LeadField_Register


DEFAULT_FIELD_QUESTION_MAP = {
    'full name': 1,
    'full_name': 1,
    'name': 1,
    'email': 2,
    'email address': 2,
    'email id': 2,
    'contact number': 3,
    'contact no': 3,
    'contact': 3,
    'phone': 3,
    'phone number': 3,
    'role applied': 4,
    'role applying for': 4,
    'role_applied': 4,
    'applied for': 4,
    'highest qualification': 5,
    'highest educational qualification': 5,
    'highest_qualification': 5,
    'qualification': 5,
    'field of study': 6,
    'field_of_study': 6,
    'specialization': 6,
    'college': 7,
    'university': 7,
    'graduation year': 8,
    'graduation_year': 8,
    'year of passout': 8,
    'academic performance': 9,
    'academic_performance': 9,
    'cgpa': 9,
    'percentage': 9,
    'has experience': 10,
    'has_experience': 10,
    'prior work experience': 10,
    'experience': 10,
    'last company': 11,
    'last_company': 11,
    'most recent company': 11,
    'last role': 12,
    'last_role': 12,
    'experience duration': 13,
    'experience_duration': 13,
    'total experience': 13,
    'skills': 14,
    'technical skills': 14,
    'top technical skills': 14,
    'notice period': 15,
    'notice_period': 15,
    'salary': 16,
    'expected salary': 16,
    'expected_salary': 16,
    'expected annual salary': 16,
    'linkedin': 17,
    'linkedin profile': 17,
    'why good fit': 18,
    'why_good_fit': 18,
}


class Command(BaseCommand):
    help = 'Map existing Registered Work lead fields to permanent interview question IDs (1-18).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--work',
            type=int,
            default=None,
            help='Optional WorkRegister ID to restrict field mapping to a single work.',
        )

    def handle(self, *args, **options):
        work_id = options.get('work')
        qs = LeadField_Register.objects.select_related(
            'work', 'client', 'lead_category__client_task'
        ).order_by('id')
        if work_id is not None:
            qs = qs.filter(
                Q(work_id=work_id)
                | Q(work__isnull=True, lead_category__client_task__work_id=work_id)
            )

        updated_count = 0
        skipped_count = 0

        with transaction.atomic():
            for field in qs:
                normalized_name = ' '.join((field.name or '').strip().lower().split())
                dirty_fields = []

                cat_task = (
                    field.lead_category.client_task
                    if field.lead_category_id and field.lead_category.client_task_id
                    else None
                )
                if not field.work_id and cat_task and cat_task.work_id:
                    field.work_id = cat_task.work_id
                    dirty_fields.append('work')
                if not field.client_id and cat_task and cat_task.client_id:
                    field.client_id = cat_task.client_id
                    dirty_fields.append('client')

                if field.question_id is not None:
                    label = QUESTION_BY_ID.get(field.question_id, ('', 'Unknown'))[1]
                    if dirty_fields:
                        field.full_clean()
                        field.save(update_fields=dirty_fields)
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'  [WORK BACKFILLED] Field #{field.id} ({field.name!r}, work_id={field.work_id}) -> '
                                f'{field.question_id} - {label}'
                            )
                        )
                        updated_count += 1
                    else:
                        self.stdout.write(
                            f'  [ALREADY MAPPED] Field #{field.id} ({field.name!r}, work_id={field.work_id}) -> '
                            f'{field.question_id} - {label}'
                        )
                        skipped_count += 1
                    continue

                target_qid = DEFAULT_FIELD_QUESTION_MAP.get(normalized_name)
                if target_qid is None:
                    if dirty_fields:
                        field.full_clean()
                        field.save(update_fields=dirty_fields)
                    self.stdout.write(
                        self.style.WARNING(
                            f'  [UNMAPPED] Field #{field.id} ({field.name!r}, work_id={field.work_id}) -> Not asked'
                        )
                    )
                    skipped_count += 1
                    continue

                if field.work_id and LeadField_Register.objects.filter(
                    work_id=field.work_id, question_id=target_qid
                ).exclude(pk=field.pk).exists():
                    self.stdout.write(
                        self.style.WARNING(
                            f'  [CONFLICT] Field #{field.id} ({field.name!r}, work_id={field.work_id}) skipped: '
                            f'question_id={target_qid} is already assigned in this work.'
                        )
                    )
                    skipped_count += 1
                    continue

                field.question_id = target_qid
                dirty_fields.append('question_id')
                field.full_clean()
                field.save(update_fields=dirty_fields)
                label = QUESTION_BY_ID[target_qid][1]
                self.stdout.write(
                    self.style.SUCCESS(
                        f'  [MAPPED] Field #{field.id} ({field.name!r}, work_id={field.work_id}) -> '
                        f'{target_qid} - {label}'
                    )
                )
                updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Done: {updated_count} field(s) mapped/updated, {skipped_count} field(s) unchanged.'
            )
        )
