import logging
from telegram import Update
from telegram.ext import ContextTypes
from ..db_sqlite import Database
from ..logging_setup import event_log
from ..utils.tg import welcome_keyboard

logger = logging.getLogger("gatebot")

async def welcome_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик приветственного сообщения с кнопкой доступа"""
    user = update.effective_user
    user_id = user.id
    username = user.username
    first_name = user.first_name

    # Сохраняем пользователя в базу
    db: Database = context.application.bot_data["db"]
    await db.upsert_user(user_id=user_id, username=username, first_name=first_name)
    await db.set_user_source(user_id, "direct")
    await db.add_event(user_id=user_id, event_type="welcome", source="direct")
    event_log(logger, "welcome", user_id, "direct", "Welcome message sent")

    # Отправляем приветственное сообщение с кнопкой
    welcome_text = (
        "🚀 Welcome to the exclusive trading community!\n\n"
        "Get access to our private channel with:\n"
        "• Exclusive trading calls\n"
        "• Market analysis\n"
        "• Expert insights\n\n"
        "Click the button below to start your verification process."
    )
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=welcome_keyboard()
    )
