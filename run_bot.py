#!/usr/bin/env python3
"""
Скрипт запуска бота для PythonAnywhere
"""
import os
import sys
from pathlib import Path

# Добавляем путь к проекту
project_path = Path(__file__).parent
sys.path.append(str(project_path))
sys.path.append(str(project_path / "src"))

# Импортируем main функцию
from main import start_bot

if __name__ == "__main__":
    print("Starting Telegram bot on PythonAnywhere...")
    start_bot()
