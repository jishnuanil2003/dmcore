import re
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import validate_email


def is_valid_email(email):
    """Return True if email is a valid email address via Django's validate_email."""
    if not email or not isinstance(email, str) or not email.strip():
        return False
    try:
        validate_email(email.strip())
        return True
    except ValidationError:
        return False


def clean_phone_digits(phone):
    """Strip spaces, dashes, parentheses and a leading plus."""
    if not phone or not isinstance(phone, str):
        return ""
    cleaned = phone.strip()
    if cleaned.startswith("+"):
        cleaned = cleaned[1:]
    return re.sub(r"[\s\-()]+", "", cleaned)


def is_valid_phone(phone):
    """Return True if phone after removing spaces, dashes and leading + is 10 to 15 digits."""
    digits = clean_phone_digits(phone)
    return bool(re.fullmatch(r"\d{10,15}", digits))


def has_valid_email_or_phone(lead):
    """Check if lead has a valid email OR a valid phone number (at least one)."""
    if not lead:
        return False
    if is_valid_email(getattr(lead, "email", None)):
        return True
    if is_valid_phone(getattr(lead, "contact", None)):
        return True
    return False


def normalize_phone_e164(phone, default_country_code=None):
    """
    Normalise phone for sending in E.164 (+<digits>).
    10 digits get the country code from DEFAULT_PHONE_COUNTRY_CODE (default '91').
    Numbers that already carry a country code (11-15 digits) keep their code.
    Refuse (raise ValueError) if it cannot be normalised.
    """
    digits = clean_phone_digits(phone)
    if not re.fullmatch(r"\d{10,15}", digits):
        raise ValueError("Invalid phone format: must be 10 to 15 digits.")

    if len(digits) == 10:
        cc = default_country_code or getattr(settings, "DEFAULT_PHONE_COUNTRY_CODE", "91")
        cc_clean = clean_phone_digits(str(cc))
        return f"+{cc_clean}{digits}"
    return f"+{digits}"


def mask_email(email):
    """Mask email for display/logs, e.g. a***@gmail.com. Never expose full email."""
    if not email or "@" not in email:
        return "***"
    user_part, domain = email.strip().split("@", 1)
    if not user_part:
        return f"***@{domain}"
    if len(user_part) == 1:
        masked_user = f"{user_part}***"
    else:
        masked_user = f"{user_part[0]}***"
    return f"{masked_user}@{domain}"


def mask_phone(phone):
    """Mask phone for display/logs, e.g. +91******3210. Never expose full phone number."""
    if not phone or not isinstance(phone, str):
        return "***"
    raw = phone.strip()
    prefix = "+" if raw.startswith("+") else ""
    digits = clean_phone_digits(raw)
    if len(digits) <= 4:
        return f"{prefix}***{digits}"
    # Keep first 2 digits (e.g. 91) and last 4 digits (e.g. 3210), mask middle with 6 asterisks
    if len(digits) >= 6:
        first = digits[:2]
        last = digits[-4:]
        return f"{prefix}{first}******{last}"
    return f"{prefix}***{digits[-4:]}"
