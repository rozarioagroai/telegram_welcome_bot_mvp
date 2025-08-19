# Vercel Python Serverless Function entrypoint
# Обрабатывает Telegram webhook и передаёт апдейты в PTB Application

import os
import json
import asyncio
from typing import Any
from telegram import Update
from telegram.error import TelegramError

# наша сборка приложения (регистрирует хэндлеры, подключает БД и т.п.)
from src.bot_app import build_app
from src.config import settings

# Создаём глобально, чтобы между вызовами не пересоздавать
_app_init_lock = asyncio.Lock()
_app: Any = None
_loop = asyncio.new_event_loop()
asyncio.set_event_loop(_loop)

async def _ensure_app() -> Any:
    global _app
    if _app is None:
        _app = await build_app()
        await _app.initialize()
    return _app

def handler(request):
    # Telegram шлёт JSON в POST
    if request.method != "POST":
        return ("OK", 200)

    try:
        data = request.get_json(force=True, silent=False)
    except Exception:
        return ("bad request", 400)

    async def _process():
        app = await _ensure_app()
        update = Update.de_json(data, app.bot)
        try:
            await app.process_update(update)
        except TelegramError:
            # не роняем функцию из-за API ошибок
            pass
        return "OK"

    # Выполняем в нашем loop
    result = _loop.run_until_complete(_process())
    return (result, 200)