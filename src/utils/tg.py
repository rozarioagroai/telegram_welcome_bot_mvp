from typing import Optional
from urllib.parse import quote_plus
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def parse_start_payload(text: str) -> str:
    """
    Extract payload from '/start <payload>'. If absent, returns 'direct'.
    """
    if not text:
        return "direct"
    parts = text.strip().split(maxsplit=1)
    if not parts:
        return "direct"
    if parts[0].startswith("/start"):
        if len(parts) > 1 and parts[1].strip():
            arg = parts[1].strip().split()[0]
            return arg
        return "direct"
    # fallback: if someone passes raw "payload", treat as payload
    return parts[0]

def human_button() -> InlineKeyboardMarkup:
    kb = [[InlineKeyboardButton(text="✅ I’m human", callback_data="captcha_ok")]]
    return InlineKeyboardMarkup(kb)

def post_captcha_keyboard(ref_url: str) -> InlineKeyboardMarkup:
    kb = [
        [InlineKeyboardButton(text="Register via my link", url=ref_url)],
        [InlineKeyboardButton(text="Use /getaccess after KYC", callback_data="noop")],
        [InlineKeyboardButton(text="I clicked register link", callback_data="clicked_ref")],
    ]
    return InlineKeyboardMarkup(kb)

def build_ref_utm(base_url: str, campaign: str, source: str) -> str:
    from urllib.parse import urlencode
    params = {
        "utm_source": "telegram",
        "utm_medium": "bot",
        "utm_campaign": campaign,
        "utm_content": source,
    }
    return f"{base_url}?{urlencode(params)}"