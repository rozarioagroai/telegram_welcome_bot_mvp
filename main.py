#!/usr/bin/env python3
"""
Telegram Bot для Koyeb - Polling режим
"""
import os
import sys
import asyncio
import logging
from pathlib import Path

# Добавляем путь к src для импорта модулей
sys.path.append(str(Path(__file__).parent / "src"))

from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from src.config import settings
from src.logging_setup import setup_logging
from src.db import Database
from src.handlers.start import start_handler
from src.handlers.access import getaccess_handler
from src.handlers.help import help_handler
from src.handlers.callbacks import captcha_ok_handler, enter_data_handler
from src.handlers.data import user_data_message_handler
from src.handlers.admin_actions import admin_approve_handler, admin_deny_handler
from src.services.throttling import Throttler
from telegram.update import Update

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def configure_channel_id(app: Application, db: Database) -> None:
    """Настройка ID канала"""
    if settings.CHANNEL_ID is None and settings.CHANNEL_USERNAME:
        existing = await db.get_kv("CHANNEL_ID")
        if existing:
            return
        try:
            chat = await app.bot.get_chat(settings.CHANNEL_USERNAME)
            await db.set_kv("CHANNEL_ID", str(chat.id))
            logger.info(f"Resolved CHANNEL_ID={chat.id} from {settings.CHANNEL_USERNAME}")
        except Exception as e:
            logger.warning(f"Could not resolve channel ID: {e}")

async def post_init(app: Application) -> None:
    """Инициализация после создания приложения"""
    try:
        db = Database(settings.DB_PATH)
        await db.connect()
        await db.migrate()
        app.bot_data["db"] = db
        app.bot_data["throttler"] = Throttler()
        app.bot_data["captcha_deadlines"] = {}
        app.bot_data["awaiting_data"] = set()
        await configure_channel_id(app, db)
        logger.info("Bot initialized successfully")
    except Exception as e:
        logger.error(f"Error during initialization: {e}")

def build_app() -> Application:
    """Создание и настройка приложения"""
    setup_logging()
    
    # Проверяем токен
    if not settings.BOT_TOKEN:
        logger.error("BOT_TOKEN not set!")
        sys.exit(1)
    
    app = Application.builder().token(settings.BOT_TOKEN).post_init(post_init).build()

    # Добавляем обработчики
    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CallbackQueryHandler(captcha_ok_handler, pattern="^captcha_ok$"))
    app.add_handler(CallbackQueryHandler(enter_data_handler, pattern="^enter_data$"))
    app.add_handler(CallbackQueryHandler(admin_approve_handler, pattern=r"^admin_approve:\d+$"))
    app.add_handler(CallbackQueryHandler(admin_deny_handler, pattern=r"^admin_deny:\d+$"))
    app.add_handler(CommandHandler("getaccess", getaccess_handler))
    app.add_handler(CommandHandler("help", help_handler))
    app.add_handler(CommandHandler("enterdata", lambda u, c: enter_data_handler(u, c)))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, user_data_message_handler))

    return app

async def main():
    """Главная функция"""
    try:
        app = build_app()
        logger.info("Starting bot in polling mode...")
        
        # Запускаем в polling режиме
        await app.initialize()
        await app.start()
        await app.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Error running bot: {e}")
        sys.exit(1)
    finally:
        try:
            await app.stop()
            await app.shutdown()
        except:
            pass

if __name__ == "__main__":
    # Запускаем бота
    asyncio.run(main())
