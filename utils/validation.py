import re


def validate_email(email: str) -> bool:
    """Validate email address format."""
    if not email:
        return False
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return bool(re.match(pattern, email.strip()))


def validate_phone(phone: str) -> bool:
    """Validate phone number (digits, optional leading +, length 7-15)."""
    if not phone:
        return False
    pattern = r"^\+?[0-9]{7,15}$"
    return bool(re.match(pattern, phone.strip()))


def validate_passport(passport: str) -> bool:
    """Validate passport number (alphanumeric, length 5-20)."""
    if not passport:
        return False
    pattern = r"^[A-Za-z0-9]{5,20}$"
    return bool(re.match(pattern, passport.strip()))


def validate_pnr(pnr: str) -> bool:
    """Validate PNR number format (e.g. AI-XXXXXX)."""
    if not pnr:
        return False
    pattern = r"^[A-Z0-9]{2,4}-[A-Z0-9]{6,}$"
    return bool(re.match(pattern, pnr.strip().upper()))
