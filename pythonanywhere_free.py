#!/usr/bin/env python3
"""
Оптимизированный скрипт для бесплатной версии PythonAnywhere
Работает короткими сессиями для экономии CPU seconds
"""
import os
import sys
import time
import asyncio
from pathlib import Path

# Устанавливаем путь к проекту
project_path = Path("/home/JohnBill/telegram_welcome_bot_mvp")
sys.path.insert(0, str(project_path))
sys.path.insert(0, str(project_path / "src"))

# Меняем рабочую директорию
os.chdir(project_path)

# Загружаем переменные окружения из файла
if (project_path / ".env").exists():
    try:
        from dotenv import load_dotenv
        load_dotenv(project_path / ".env")
    except ImportError:
        print("python-dotenv not installed, loading .env manually")
        with open(project_path / ".env") as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value

def run_bot_session():
    """Запуск бота на короткую сессию (30-60 секунд)"""
    print("Starting Telegram bot session...")
    
    try:
        # Импортируем только когда нужно
        from telegram.ext import Application
        from src.config import settings
        from src.logging_setup import setup_logging
        from src.db_sqlite import Database
        from src.handlers.welcome import welcome_handler
        from src.handlers.access_button import start_access_handler
        from src.handlers.callbacks import captcha_ok_handler, enter_data_handler
        from src.handlers.data import user_data_message_handler
        from src.handlers.admin_actions import admin_approve_handler, admin_deny_handler
        from src.services.throttling import Throttler
        
        async def run_session():
            # Создаем приложение
            app = Application.builder().token(settings.BOT_TOKEN).build()
            
            # Инициализируем базу данных
            db = Database(settings.DB_PATH)
            await db.connect()
            await db.migrate()
            
            # Настраиваем bot_data
            app.bot_data["db"] = db
            app.bot_data["throttler"] = Throttler()
            app.bot_data["captcha_deadlines"] = {}
            app.bot_data["awaiting_data"] = set()
            
            # Добавляем обработчики
            from telegram.ext import CommandHandler, CallbackQueryHandler, MessageHandler, filters
            app.add_handler(CommandHandler("start", welcome_handler))
            app.add_handler(CallbackQueryHandler(start_access_handler, pattern="^start_access$"))
            app.add_handler(CallbackQueryHandler(captcha_ok_handler, pattern="^captcha_ok$"))
            app.add_handler(CallbackQueryHandler(enter_data_handler, pattern="^enter_data$"))
            app.add_handler(CallbackQueryHandler(admin_approve_handler, pattern=r"^admin_approve:\d+$"))
            app.add_handler(CallbackQueryHandler(admin_deny_handler, pattern=r"^admin_deny:\d+$"))
            app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, user_data_message_handler))
            
            # Инициализируем приложение
            await app.initialize()
            await app.start()
            
            print("Bot session started, processing updates...")
            
            # Обрабатываем сообщения в течение 45 секунд
            start_time = time.time()
            offset = 0
            
            while time.time() - start_time < 45:  # 45 секунд сессия
                try:
                    updates = await app.updater.bot.get_updates(offset=offset, timeout=10)
                    if updates:
                        for update in updates:
                            await app.process_update(update)
                            offset = update.update_id + 1
                        print(f"Processed {len(updates)} updates")
                    await asyncio.sleep(1)
                except Exception as e:
                    print(f"Error processing updates: {e}")
                    await asyncio.sleep(2)
            
            print("Session completed, shutting down...")
            await app.stop()
            await app.shutdown()
            
        # Запускаем сессию
        asyncio.run(run_session())
        
    except Exception as e:
        print(f"Bot session failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=== PythonAnywhere Free Bot Session ===")
    run_bot_session()
    print("=== Session Ended ===")
