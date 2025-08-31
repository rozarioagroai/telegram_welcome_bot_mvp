#!/usr/bin/env python3
"""
Скрипт для ручного тестирования бота в консоли PythonAnywhere
Позволяет запустить бота на определенное время для тестирования
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

# Загружаем переменные окружения
if (project_path / ".env").exists():
    try:
        from dotenv import load_dotenv
        load_dotenv(project_path / ".env")
    except ImportError:
        print("Loading .env manually...")
        with open(project_path / ".env") as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value

def main():
    print("🤖 Telegram Bot Manual Test")
    print("=" * 40)
    
    # Выбор режима запуска
    print("Выберите режим запуска:")
    print("1. Быстрый тест (30 секунд)")
    print("2. Средний тест (2 минуты)")
    print("3. Длительный тест (5 минут)")
    print("4. Проверка конфигурации")
    print("5. Проверка базы данных")
    
    try:
        choice = input("Введите номер (1-5): ").strip()
    except KeyboardInterrupt:
        print("\n👋 Выход из программы")
        return
    
    if choice == "1":
        run_bot_test(30)
    elif choice == "2":
        run_bot_test(120)
    elif choice == "3":
        run_bot_test(300)
    elif choice == "4":
        check_config()
    elif choice == "5":
        check_database()
    else:
        print("❌ Неверный выбор")

def run_bot_test(duration_seconds):
    """Запуск бота на указанное время"""
    print(f"🚀 Запуск бота на {duration_seconds} секунд...")
    
    try:
        from telegram.ext import Application
        from src.config import settings
        from src.db_sqlite import Database
        from src.handlers.welcome import welcome_handler
        from src.handlers.access_button import start_access_handler
        from src.handlers.callbacks import captcha_ok_handler, enter_data_handler
        from src.handlers.data import user_data_message_handler
        from src.handlers.admin_actions import admin_approve_handler, admin_deny_handler
        from src.services.throttling import Throttler
        
        async def run_test():
            print("📡 Создание приложения...")
            app = Application.builder().token(settings.BOT_TOKEN).build()
            
            print("💾 Инициализация базы данных...")
            db = Database(settings.DB_PATH)
            await db.connect()
            await db.migrate()
            
            app.bot_data["db"] = db
            app.bot_data["throttler"] = Throttler()
            app.bot_data["captcha_deadlines"] = {}
            app.bot_data["awaiting_data"] = set()
            
            print("🔧 Настройка обработчиков...")
            from telegram.ext import CommandHandler, CallbackQueryHandler, MessageHandler, filters
            app.add_handler(CommandHandler("start", welcome_handler))
            app.add_handler(CallbackQueryHandler(start_access_handler, pattern="^start_access$"))
            app.add_handler(CallbackQueryHandler(captcha_ok_handler, pattern="^captcha_ok$"))
            app.add_handler(CallbackQueryHandler(enter_data_handler, pattern="^enter_data$"))
            app.add_handler(CallbackQueryHandler(admin_approve_handler, pattern=r"^admin_approve:\d+$"))
            app.add_handler(CallbackQueryHandler(admin_deny_handler, pattern=r"^admin_deny:\d+$"))
            app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, user_data_message_handler))
            
            await app.initialize()
            await app.start()
            
            print(f"✅ Бот запущен! Работает {duration_seconds} секунд...")
            print("💬 Можете тестировать бота в Telegram")
            print("⏱️  Прогресс:", end=" ")
            
            start_time = time.time()
            offset = 0
            message_count = 0
            
            while time.time() - start_time < duration_seconds:
                try:
                    updates = await app.updater.bot.get_updates(offset=offset, timeout=5)
                    if updates:
                        for update in updates:
                            await app.process_update(update)
                            offset = update.update_id + 1
                            message_count += 1
                        print(f"📨 +{len(updates)}", end=" ")
                    
                    # Показываем прогресс
                    elapsed = int(time.time() - start_time)
                    if elapsed % 10 == 0:
                        remaining = duration_seconds - elapsed
                        print(f"({remaining}s)", end=" ")
                    
                    await asyncio.sleep(1)
                except KeyboardInterrupt:
                    print("\n🛑 Остановка по Ctrl+C")
                    break
                except Exception as e:
                    print(f"\n⚠️ Ошибка: {e}")
                    await asyncio.sleep(2)
            
            print(f"\n📊 Статистика: обработано {message_count} сообщений")
            print("🔄 Остановка бота...")
            await app.stop()
            await app.shutdown()
            print("✅ Бот остановлен")
        
        asyncio.run(run_test())
        
    except Exception as e:
        print(f"❌ Ошибка запуска: {e}")
        import traceback
        traceback.print_exc()

def check_config():
    """Проверка конфигурации"""
    print("🔍 Проверка конфигурации...")
    
    try:
        from src.config import settings
        
        print(f"✅ BOT_TOKEN: {'✓ установлен' if settings.BOT_TOKEN else '❌ не установлен'}")
        print(f"✅ CHANNEL_USERNAME: {settings.CHANNEL_USERNAME or '❌ не установлен'}")
        print(f"✅ ADMIN_IDS: {settings.ADMIN_IDS or '❌ не установлены'}")
        print(f"✅ DB_PATH: {settings.DB_PATH}")
        print(f"✅ LOG_LEVEL: {settings.LOG_LEVEL}")
        
        if settings.BOT_TOKEN:
            print("🤖 Тестирование подключения к Telegram API...")
            import asyncio
            from telegram import Bot
            
            async def test_bot():
                bot = Bot(settings.BOT_TOKEN)
                try:
                    me = await bot.get_me()
                    print(f"✅ Бот подключен: @{me.username} ({me.first_name})")
                except Exception as e:
                    print(f"❌ Ошибка подключения: {e}")
            
            asyncio.run(test_bot())
        
    except Exception as e:
        print(f"❌ Ошибка проверки: {e}")

def check_database():
    """Проверка базы данных"""
    print("💾 Проверка базы данных...")
    
    try:
        from src.config import settings
        from src.db_sqlite import Database
        
        async def test_db():
            db = Database(settings.DB_PATH)
            await db.connect()
            await db.migrate()
            
            print(f"✅ База данных: {settings.DB_PATH}")
            
            # Проверяем таблицы
            import sqlite3
            conn = sqlite3.connect(settings.DB_PATH)
            cur = conn.cursor()
            
            cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cur.fetchall()
            print(f"✅ Таблицы: {[t[0] for t in tables]}")
            
            # Считаем записи
            for table in ['users', 'events', 'submissions']:
                try:
                    cur.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cur.fetchone()[0]
                    print(f"📊 {table}: {count} записей")
                except:
                    print(f"⚠️ {table}: таблица не найдена")
            
            conn.close()
        
        asyncio.run(test_db())
        
    except Exception as e:
        print(f"❌ Ошибка проверки БД: {e}")

if __name__ == "__main__":
    main()
