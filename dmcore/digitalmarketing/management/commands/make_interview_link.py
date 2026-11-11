import json
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from digitalmarketing.models import Leads
from digitalmarketing.utils import make_interview_link


class Command(BaseCommand):
    help = 'Print an interview URL and its candidate/questions JSON for a lead.'

    def add_arguments(self, parser):
        parser.add_argument('lead_id', type=int)

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError('make_interview_link can only run when DEBUG is true.')

        lead = Leads.objects.select_related('work').filter(pk=options['lead_id']).first()
        if not lead:
            raise CommandError(f"Lead {options['lead_id']} was not found.")

        link, payload = make_interview_link(lead)
        self.stdout.write(link)
        self.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2))
