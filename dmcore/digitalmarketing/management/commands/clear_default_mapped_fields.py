from django.core.management.base import BaseCommand
from django.db import transaction

from digitalmarketing.interview_questions import DEFAULT_MAPPED_QUESTION_IDS, QUESTION_BY_ID
from digitalmarketing.models import LeadField_Register


class Command(BaseCommand):
    help = 'Clear question_id on LeadField_Register rows mapped to default questions (1, 2, 3, 19) or invalid IDs.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--apply',
            action='store_true',
            help='Actually update the database (clears question_id to NULL). Default is dry-run.',
        )

    def handle(self, *args, **options):
        apply_changes = options.get('apply', False)
        mode_str = 'APPLY' if apply_changes else 'DRY RUN'
        self.stdout.write(f'Running clear_default_mapped_fields ({mode_str})...')

        valid_custom_qids = set(QUESTION_BY_ID.keys()) - set(DEFAULT_MAPPED_QUESTION_IDS)

        fields_to_clear = LeadField_Register.objects.filter(
            question_id__isnull=False
        ).exclude(
            question_id__in=valid_custom_qids
        ).select_related('work', 'client').order_by('id')

        count = fields_to_clear.count()
        if count == 0:
            self.stdout.write(self.style.SUCCESS('No fields mapped to default or invalid question IDs found.'))
            return

        self.stdout.write(f'Found {count} field(s) mapped to default/invalid question IDs:\n')
        self.stdout.write(f"{'Field ID':<10} | {'Field Name':<25} | {'Question ID':<12} | {'Work':<20} | {'Client':<20}")
        self.stdout.write('-' * 95)

        for field in fields_to_clear:
            work_name = str(field.work) if field.work else 'N/A'
            client_name = str(field.client) if field.client else 'N/A'
            self.stdout.write(
                f"{field.id:<10} | {(field.name or ''):<25} | {field.question_id:<12} | {work_name:<20} | {client_name:<20}"
            )

        if apply_changes:
            with transaction.atomic():
                updated = fields_to_clear.update(question_id=None)
            self.stdout.write(self.style.SUCCESS(f'\nSuccessfully cleared question_id on {updated} field(s).'))
        else:
            self.stdout.write(self.style.WARNING(f'\nDry run only. {count} field(s) would be cleared. Run with --apply to execute.'))
