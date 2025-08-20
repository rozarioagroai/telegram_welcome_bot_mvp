#!/usr/bin/env python3
"""
Telegram Bot для Koyeb - Упрощенная версия
"""
import os
import sys
import asyncio
import logging
import threading
import time
from pathlib import Path

# Добавляем путь к src для импорта модулей
sys.path.append(str(Path(__file__).parent / "src"))

from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from telegram import Update
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
        logger.info("Starting post_init...")
        
        # Проверяем настройки
        logger.info(f"DB_PATH: {settings.DB_PATH}")
        logger.info(f"BOT_TOKEN: {'SET' if settings.BOT_TOKEN else 'NOT SET'}")
        
        # Создаем базу данных
        db = Database(settings.DB_PATH)
        logger.info("Database object created")
        
        await db.connect()
        logger.info("Database connected")
        
        await db.migrate()
        logger.info("Database migrated")
        
        # Сохраняем в bot_data
        app.bot_data["db"] = db
        app.bot_data["throttler"] = Throttler()
        app.bot_data["captcha_deadlines"] = {}
        app.bot_data["awaiting_data"] = set()
        
        logger.info(f"bot_data keys: {list(app.bot_data.keys())}")
        logger.info(f"db in bot_data: {'db' in app.bot_data}")
        
        await configure_channel_id(app, db)
        logger.info("Bot initialized successfully")
        
    except Exception as e:
        logger.error(f"Error during initialization: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise  # Перебрасываем ошибку для диагностики

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

def run_polling():
    """Запуск polling в отдельном потоке"""
    try:
        # Создаем новый event loop для этого потока
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def run():
            try:
                logger.info("Building app...")
                app = build_app()
                logger.info("App built successfully")
                
                logger.info("Starting bot in polling mode...")
                
                # ВАЖНО: Вызываем post_init вручную
                logger.info("Calling post_init...")
                await post_init(app)
                logger.info("post_init completed")
                
                # Проверяем bot_data после post_init
                logger.info(f"bot_data after post_init: {list(app.bot_data.keys())}")
                logger.info(f"db in bot_data: {'db' in app.bot_data}")
                
                await app.initialize()
                logger.info("App initialized")
                
                await app.start()
                logger.info("App started")
                
                # Простой polling без signal handling
                while True:
                    try:
                        updates = await app.updater.bot.get_updates()
                        for update in updates:
                            await app.process_update(update)
                        await asyncio.sleep(1)  # Пауза между проверками
                    except Exception as e:
                        logger.error(f"Error processing updates: {e}")
                        await asyncio.sleep(5)  # Пауза при ошибке
                
            except Exception as e:
                logger.error(f"Error in polling: {e}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
            finally:
                try:
                    await app.stop()
                    await app.shutdown()
                except:
                    pass
        
        # Запускаем в этом loop
        loop.run_until_complete(run())
        
    except Exception as e:
        logger.error(f"Error in polling thread: {e}")

def start_bot():
    """Запуск бота без конфликтующих event loop"""
    try:
        logger.info("Starting bot in background thread...")
        
        # Запускаем в отдельном потоке
        bot_thread = threading.Thread(target=run_polling, daemon=True)
        bot_thread.start()
        
        logger.info("Bot started successfully in background thread")
        
        # Держим основной поток живым
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Shutting down...")
            
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Запускаем бота
    start_bot()
