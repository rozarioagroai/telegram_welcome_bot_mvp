#!/usr/bin/env python3
"""
Файл для запуска бота через PythonAnywhere Tasks
"""
import os
import sys
from pathlib import Path

# Устанавливаем путь к проекту
project_path = Path("/home/JohnBill/telegram_welcome_bot_mvp")  # Путь к клонированному репозиторию
sys.path.insert(0, str(project_path))
sys.path.insert(0, str(project_path / "src"))

# Меняем рабочую директорию
os.chdir(project_path)

# Загружаем переменные окружения из файла
if (project_path / ".env").exists():
    from dotenv import load_dotenv
    load_dotenv(project_path / ".env")

# Запускаем бота
from main import start_bot

if __name__ == "__main__":
    print("Starting Telegram bot via PythonAnywhere Task...")
    try:
        start_bot()
    except KeyboardInterrupt:
        print("Bot stopped by user")
    except Exception as e:
        print(f"Bot crashed: {e}")
        import traceback
        traceback.print_exc()
