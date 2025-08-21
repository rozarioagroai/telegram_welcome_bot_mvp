import logging
import time
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from ..db_sqlite import Database
from ..logging_setup import event_log
from ..services.checklist import send_checklist

logger = logging.getLogger("gatebot")

GUIDE_TEXT = (
    "Step-by-Step Guide\n\n"
    "1. Sign up on Axiom \n"
    "Use this link: Axiom Pro (http://axiom.trade/@danfoht)\n"
    "During registration, make sure to enter the referral code: danfoht (this is mandatory!).\n\n"
    "2. Press \"Enter data\" and send details to the bot\n"
    "In the bot chat, provide:\n"
    "• The email you used to register on Axiom\n"
    "• Your Telegram @username  \n\n"
    "The system will check your registration and, if everything is correct, you’ll automatically receive entry to the exclusive private Telegram channel with trading calls and analytics."
)

ALMOST_THERE_TEXT = (
    "Almost there!\n"
    "Just one last step to get inside:\n"
    "Drop your Axiom registration email and your Telegram @username in a single message right here.\n\n"
    "Once you send it, the bot will verify and unlock your access to the private channel."
)

async def captcha_ok_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    db: Database = context.application.bot_data["db"]
    deadlines: dict = context.application.bot_data["captcha_deadlines"]

    user = update.effective_user
    user_id = user.id
    source = await db.get_user_source(user_id) or "direct"

    now = int(time.time())
    deadline = deadlines.get(user_id)

    if deadline is None or now > deadline:
        try:
            await update.callback_query.edit_message_text("Time’s up. Send /start again.")
        except Exception:
            pass
        await update.callback_query.answer()
        return

    await db.add_event(user_id=user_id, event_type="captcha_ok", source=source)
    event_log(logger, "captcha_ok", user_id, source, "Captcha passed")
    deadlines.pop(user_id, None)

    await update.callback_query.answer("Verified!")
    await send_checklist(update, context, db=db, source=source)

    # Send your Step-by-Step Guide with "Enter data"
    enter_kb = InlineKeyboardMarkup([[InlineKeyboardButton("Enter data", callback_data="enter_data")]])
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=GUIDE_TEXT,
        reply_markup=enter_kb,
    )

async def enter_data_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Callback for 'Enter data' and also reused by 'Try again'."""
    awaiting: set[int] = context.application.bot_data["awaiting_data"]
    user_id = update.effective_user.id
    awaiting.add(user_id)
    try:
        await update.callback_query.answer()
    except Exception:
        pass
    try:
        await update.callback_query.edit_message_reply_markup(reply_markup=None)
    except Exception:
        pass
    await context.bot.send_message(chat_id=update.effective_chat.id, text=ALMOST_THERE_TEXT)