import logging
from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import TelegramError
from ..config import settings
from ..db_sqlite import Database
from ..logging_setup import event_log
from ..services.throttling import Throttler
from ..services.invites import create_one_time_invite

logger = logging.getLogger("gatebot")

async def getaccess_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    db: Database = context.application.bot_data["db"]
    throttler: Throttler = context.application.bot_data["throttler"]

    user = update.effective_user
    user_id = user.id

    allowed, retry_after = throttler.check(user_id, "getaccess", settings.GETACCESS_THROTTLE_SECONDS)
    if not allowed:
        await update.message.reply_text(f"Too fast, try later ({retry_after}s).")
        return

    has_captcha = await db.has_valid_captcha(user_id)
    source = await db.get_user_source(user_id) or "direct"
    if not has_captcha:
        await update.message.reply_text("You need to pass captcha first. Send /start.")
        return

    channel_id = settings.CHANNEL_ID
    if channel_id is None:
        kv_id = await db.get_kv("CHANNEL_ID")
        if kv_id:
            try:
                channel_id = int(kv_id)
            except ValueError:
                channel_id = None
    if channel_id is None:
        await update.message.reply_text("Channel ID is not configured. Ask admin.")
        return

    try:
        link = await create_one_time_invite(
            bot=context.bot,
            db=db,
            chat_id=channel_id,
            ttl_seconds=settings.INVITE_TTL_SECONDS,
            user_id=user_id,
        )
    except TelegramError as e:
        event_log(logger, "getaccess_error", user_id, source, f"Failed to create invite: {e!r}")
        await update.message.reply_text("Could not create invite now. Please try later.")
        return

    await db.add_event(user_id=user_id, event_type="getaccess_issued", source=source)
    event_log(logger, "getaccess_issued", user_id, source, "Invite issued")
    await update.message.reply_text(f"Here is your one-time invite (expires soon):\n{link}")