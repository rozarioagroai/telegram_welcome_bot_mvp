import logging
import time
from telegram import Update
from telegram.ext import ContextTypes
from ..config import settings
from ..db import Database
from ..logging_setup import event_log
from ..services.throttling import Throttler
from ..utils.tg import parse_start_payload, human_button

logger = logging.getLogger("gatebot")

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    db: Database = context.application.bot_data["db"]
    throttler: Throttler = context.application.bot_data["throttler"]
    captcha_deadlines: dict = context.application.bot_data["captcha_deadlines"]

    user = update.effective_user
    user_id = user.id
    username = user.username
    first_name = user.first_name

    allowed, retry_after = throttler.check(user_id, "start", settings.START_THROTTLE_SECONDS)
    if not allowed:
        await update.message.reply_text(f"Too fast, try later ({retry_after}s).")
        return

    await db.upsert_user(user_id=user_id, username=username, first_name=first_name)

    text = update.message.text or ""
    source = parse_start_payload(text)
    await db.set_user_source(user_id, source)
    await db.add_event(user_id=user_id, event_type="start", source=source)
    event_log(logger, "start", user_id, source, "Start received")

    deadline = int(time.time()) + settings.CAPTCHA_TTL_SECONDS
    captcha_deadlines[user_id] = deadline

    await update.message.reply_text(
        "Please confirm you are human within 60 seconds.",
        reply_markup=human_button(),
    )