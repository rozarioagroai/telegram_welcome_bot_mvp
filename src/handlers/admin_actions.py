import logging
from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import TelegramError
from ..config import settings
from ..db import Database
from ..services.invites import create_one_time_invite

logger = logging.getLogger("gatebot")

APPROVED_TEXT = (
    "🟢 Access Granted!\n"
    "You now have full entry to the DanielleFoSOL private channel with exclusive calls and analytics.\n\n"
    "Here’s your link: {link}\n\n"
    "Welcome aboard — you’re officially part of our community! 🚀"
)
DENIED_TEXT = (
    "🔴 Access Denied\n"
    "It looks like you’re not registered under the referral code or you’ve entered incorrect details.\n\n"
    "Please double-check:\n"
    "• Make sure you signed up on Axiom using the referral code danfoht\n"
    "• Confirm you’re sending the same email you used for Axiom registration\n"
    "• Include your correct Telegram @username\n\n"
    "Once you fix this, send your details again to unlock access."
)

def _is_admin(user_id: int) -> bool:
    return user_id in (settings.ADMIN_IDS or [])

async def _resolve_channel_id(db: Database) -> int | None:
    cid = settings.CHANNEL_ID
    if cid is not None:
        return cid
    kv = await db.get_kv("CHANNEL_ID")
    return int(kv) if kv else None

async def admin_approve_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    cq = update.callback_query
    admin_id = update.effective_user.id
    await cq.answer()

    if not _is_admin(admin_id):
        await cq.edit_message_text("Not allowed.")
        return

    # parse submission_id
    try:
        _, sid = cq.data.split(":", 1)
        submission_id = int(sid)
    except Exception:
        await cq.edit_message_text("Invalid submission id.")
        return

    db: Database = context.application.bot_data["db"]
    sub = await db.get_submission_by_id(submission_id)
    if not sub:
        await cq.edit_message_text("Submission not found.")
        return
    if sub["status"] != "pending":
        await cq.edit_message_text(f"Already processed: {sub['status']}")
        return

    channel_id = await _resolve_channel_id(db)
    if channel_id is None:
        await cq.edit_message_text("CHANNEL_ID not configured.")
        return

    user_id = int(sub["user_id"])
    try:
        link = await create_one_time_invite(
            bot=context.bot,
            db=db,
            chat_id=channel_id,
            ttl_seconds=settings.INVITE_TTL_SECONDS,
            user_id=user_id,
        )
        await context.bot.send_message(chat_id=user_id, text=APPROVED_TEXT.format(link=link))
        await db.update_submission_status(submission_id, "approved")
        await db.add_event(user_id=user_id, event_type="manual_approved", source=sub["source"])
        await cq.edit_message_text(f"Approved and invited user {user_id}.")
    except TelegramError as e:
        logger.exception("Invite creation/send failed")
        await cq.edit_message_text(f"Failed to invite: {e!r}")

async def admin_deny_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    cq = update.callback_query
    admin_id = update.effective_user.id
    await cq.answer()

    if not _is_admin(admin_id):
        await cq.edit_message_text("Not allowed.")
        return

    try:
        _, sid = cq.data.split(":", 1)
        submission_id = int(sid)
    except Exception:
        await cq.edit_message_text("Invalid submission id.")
        return

    db: Database = context.application.bot_data["db"]
    sub = await db.get_submission_by_id(submission_id)
    if not sub:
        await cq.edit_message_text("Submission not found.")
        return
    if sub["status"] != "pending":
        await cq.edit_message_text(f"Already processed: {sub['status']}")
        return

    user_id = int(sub["user_id"])
    from telegram import InlineKeyboardMarkup, InlineKeyboardButton
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("Try again", callback_data="enter_data")]])
    await context.bot.send_message(chat_id=user_id, text=DENIED_TEXT, reply_markup=kb)
    await db.update_submission_status(submission_id, "denied")
    await db.add_event(user_id=user_id, event_type="manual_denied", source=sub["source"])
    await cq.edit_message_text(f"Denied user {user_id}.")