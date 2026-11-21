from django.core.management.base import BaseCommand
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Send a sample interview invitation test email to <address>."

    def add_arguments(self, parser):
        parser.add_argument('address', type=str, help='Recipient email address')

    def handle(self, *args, **options):
        recipient = options['address'].strip()
        company_name = getattr(settings, 'COMPANY_NAME', 'Altos Technologies')
        subject = f"Your interview invitation from {company_name}"
        context = {
            'candidate_name': 'Test Candidate',
            'company_name': company_name,
            'link': 'https://website132.altostechnologies.in/interview/sample-token',
        }
        body = render_to_string('emails/interview_invite.txt', context)
        html_body = render_to_string('emails/interview_invite.html', context)

        email = EmailMultiAlternatives(
            subject=subject,
            body=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient],
            reply_to=[settings.DEFAULT_FROM_EMAIL],
        )
        email.attach_alternative(html_body, 'text/html')

        try:
            sent_count = email.send(fail_silently=False)
            if sent_count:
                self.stdout.write(self.style.SUCCESS(f"Successfully sent test email to {recipient}"))
            else:
                self.stderr.write(self.style.ERROR("Failed: 0 emails were sent"))
        except Exception as exc:
            # Print ONLY the error type (no secrets)
            err_type = type(exc).__name__
            self.stderr.write(self.style.ERROR(f"Failed to send email: {err_type}"))
