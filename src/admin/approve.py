import argparse
import asyncio
import logging
from telegram import Bot, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.error import TelegramError
from ..config import settings
from ..db_sqlite import Database
from ..services.invites import create_one_time_invite

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(asctime)s %(message)s")
logger = logging.getLogger("approve")

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

async def approve(user_id: int) -> None:
    db = Database(settings.DB_PATH)
    await db.connect()
    await db.migrate()
    bot = Bot(settings.BOT_TOKEN)

    # channel id
    channel_id = settings.CHANNEL_ID
    if channel_id is None:
        kv = await db.get_kv("CHANNEL_ID")
        channel_id = int(kv) if kv else None
    if channel_id is None:
        raise RuntimeError("CHANNEL_ID is not configured")

    # latest pending submission
    sub = await db.get_latest_pending_submission_by_user(user_id)
    if not sub:
        logger.info(f"No pending submission for user {user_id}")
        await db.close()
        return

    link = await create_one_time_invite(bot, db, channel_id, settings.INVITE_TTL_SECONDS, user_id)
    await bot.send_message(chat_id=user_id, text=APPROVED_TEXT.format(link=link))
    await db.update_submission_status(int(sub["id"]), "approved")
    await db.add_event(user_id=user_id, event_type="manual_approved", source=sub["source"])
    await db.close()
    logger.info(f"Approved and invited user {user_id}")

async def deny(user_id: int) -> None:
    db = Database(settings.DB_PATH)
    await db.connect()
    await db.migrate()
    bot = Bot(settings.BOT_TOKEN)

    sub = await db.get_latest_pending_submission_by_user(user_id)
    if not sub:
        logger.info(f"No pending submission for user {user_id}")
        await db.close()
        return

    kb = InlineKeyboardMarkup([[InlineKeyboardButton("Try again", callback_data="enter_data")]])
    await bot.send_message(chat_id=user_id, text=DENIED_TEXT, reply_markup=kb)
    await db.update_submission_status(int(sub["id"]), "denied")
    await db.add_event(user_id=user_id, event_type="manual_denied", source=sub["source"])
    await db.close()
    logger.info(f"Denied user {user_id}")

def main():
    parser = argparse.ArgumentParser(description="Approve or deny user submission and notify them")
    g = parser.add_mutually_exclusive_group(required=True)
    g.add_argument("--approve", action="store_true", help="approve latest pending submission by user")
    g.add_argument("--deny", action="store_true", help="deny latest pending submission by user")
    parser.add_argument("--user", type=int, required=True, help="target user_id")
    args = parser.parse_args()
    if args.approve:
        asyncio.run(approve(args.user))
    else:
        asyncio.run(deny(args.user))

if __name__ == "__main__":
    main()