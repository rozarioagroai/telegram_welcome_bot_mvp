import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from ..db import Database
from ..logging_setup import event_log
from ..utils.parse import extract_email_and_username
from ..config import settings

logger = logging.getLogger("gatebot")

async def user_data_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    awaiting: set[int] = context.application.bot_data["awaiting_data"]
    if update.effective_user.id not in awaiting:
        return

    user = update.effective_user
    user_id = user.id
    text = update.message.text or ""
    email, tg_username = extract_email_and_username(text)

    if not email or not tg_username:
        await update.message.reply_text("Please send both your email and your Telegram @username in one message.")
        return

    db: Database = context.application.bot_data["db"]
    source = await db.get_user_source(user_id) or "direct"
    submission_id = await db.insert_submission(user_id=user_id, email=email, tg_username=tg_username, source=source)
    awaiting.discard(user_id)

    await db.add_event(user_id=user_id, event_type="user_data_submitted", source=source)
    event_log(logger, "user_data_submitted", user_id, source, f"Submission id={submission_id}")
    await update.message.reply_text(
        "Got it!\nWe’re now verifying your registration to grant you full access to the private channel. "
        "The check may take a few minutes — please be patient while we confirm your registration."
    )

    # Notify admins
    if settings.ADMIN_IDS:
        text_admin = (
            "New submission received\n"
            f"submission_id: {submission_id}\n"
            f"user_id: {user_id}\n"
            f"source: {source}\n"
            f"email: {email}\n"
            f"username: {tg_username}\n\n"
            "Approve or Deny below:"
        )
        kb = InlineKeyboardMarkup(
            [[
                InlineKeyboardButton("Approve", callback_data=f"admin_approve:{submission_id}"),
                InlineKeyboardButton("Deny", callback_data=f"admin_deny:{submission_id}"),
            ]]
        )
        for admin_id in settings.ADMIN_IDS:
            try:
                await context.bot.send_message(chat_id=admin_id, text=text_admin, reply_markup=kb)
            except Exception as e:
                logger.warning(f"Failed to notify admin {admin_id}: {e!r}")