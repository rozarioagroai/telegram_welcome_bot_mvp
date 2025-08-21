import re
from typing import Optional, Tuple

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
USERNAME_RE = re.compile(r"@([A-Za-z0-9_]{2,})")

def extract_email_and_username(text: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Returns (email, @username) if found, else (None, None).
    Accepts any order and extra text.
    """
    email_match = EMAIL_RE.search(text or "")
    user_match = USERNAME_RE.search(text or "")
    email = email_match.group(0) if email_match else None
    username = f"@{user_match.group(1)}" if user_match else None
    
    # Debug logging
    import logging
    logger = logging.getLogger("gatebot")
    logger.info(f"Parsing text: '{text}' -> email: {email}, username: {username}")
    
    return email, username