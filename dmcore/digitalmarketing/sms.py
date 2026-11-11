import os
import sys
from django.conf import settings
from .validators import mask_phone


class BaseSMSBackend:
    """Base interface for SMS providers."""

    def send_sms(self, to_phone: str, message: str) -> tuple[bool, str]:
        """
        Send an SMS.
        Returns:
            (success: bool, info_or_error_message: str)
        """
        raise NotImplementedError("Subclasses must implement send_sms")


class ConsoleSMSBackend(BaseSMSBackend):
    """
    Console backend: prints the message to stdout, used when DEBUG and nothing is
    configured. Clearly reports that nothing was really sent (like Django's console email backend).
    Never logs or prints full phone numbers (masks them).
    """

    def send_sms(self, to_phone: str, message: str) -> tuple[bool, str]:
        masked = mask_phone(to_phone)
        sys.stdout.write(
            f"--------------------------------------------------\n"
            f"[SMS CONSOLE BACKEND - NOT ACTUALLY SENT]\n"
            f"To: {masked}\n"
            f"Text: {message}\n"
            f"--------------------------------------------------\n"
        )
        sys.stdout.flush()
        return True, f"Console SMS simulated to {masked} (not actually sent)"


class LocmemSMSBackend(BaseSMSBackend):
    """In-memory backend for tests. Messages are captured in `outbox`."""

    outbox = []

    def send_sms(self, to_phone: str, message: str) -> tuple[bool, str]:
        self.outbox.append({
            "to": to_phone,
            "message": message,
        })
        masked = mask_phone(to_phone)
        return True, f"SMS sent to {masked}"

    @classmethod
    def reset(cls):
        cls.outbox.clear()


# Global locmem outbox accessor for easy testing (like mail.outbox)
locmem_outbox = LocmemSMSBackend.outbox


def get_sms_backend() -> BaseSMSBackend:
    """Instantiate and return the configured SMS backend."""
    backend_name = getattr(settings, "SMS_BACKEND", os.environ.get("SMS_BACKEND", "console")).lower()
    if backend_name in ("locmem", "memory"):
        return LocmemSMSBackend()
    # Default is console backend
    return ConsoleSMSBackend()
