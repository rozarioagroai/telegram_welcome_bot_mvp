import logging
import time
from telegram import Update
from telegram.ext import ContextTypes
from ..config import settings
from ..db_sqlite import Database
from ..logging_setup import event_log
from ..services.throttling import Throttler
from ..utils.tg import human_button

logger = logging.getLogger("gatebot")

async def start_access_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик кнопки 'Get Access to Private Channel'"""
    db: Database = context.application.bot_data["db"]
    throttler: Throttler = context.application.bot_data["throttler"]
    captcha_deadlines: dict = context.application.bot_data["captcha_deadlines"]

    user = update.effective_user
    user_id = user.id

    # Проверяем throttling
    allowed, retry_after = throttler.check(user_id, "start", settings.START_THROTTLE_SECONDS)
    if not allowed:
        await update.callback_query.answer(f"Too fast, try later ({retry_after}s).")
        return

    # Логируем событие
    await db.add_event(user_id=user_id, event_type="start_access", source="direct")
    event_log(logger, "start_access", user_id, "direct", "Access button clicked")

    # Устанавливаем deadline для капчи
    deadline = int(time.time()) + settings.CAPTCHA_TTL_SECONDS
    captcha_deadlines[user_id] = deadline

    # Безопасно отвечаем на callback query
    try:
        await update.callback_query.answer()
    except Exception as e:
        logger.warning(f"Failed to answer callback query: {e}")

    # Безопасно отправляем сообщение с капчей
    try:
        await update.callback_query.edit_message_text(
            "Please confirm you are human within 60 seconds.",
            reply_markup=human_button(),
        )
    except Exception:
        await context.bot.send_message(
            chat_id=user_id,
            text="Please confirm you are human within 60 seconds.",
            reply_markup=human_button(),
        )
