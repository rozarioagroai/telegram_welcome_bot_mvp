import os, asyncio
from starlette.applications import Starlette
from starlette.responses import PlainTextResponse, JSONResponse
from starlette.routing import Route
from starlette.requests import Request
from telegram import Update
from src.bot_app import build_app  # ваш сборщик PTB-приложения

_app = None
_init_lock = asyncio.Lock()  # защитим одноразовую инициализацию

async def ensure_app():
    global _app
    if _app is None:
        async with _init_lock:
            if _app is None:
                _app = await build_app()
                await _app.initialize()
    return _app

async def webhook(request: Request):
    # GET — удобный health-check (браузером увидите "ok")
    if request.method != "POST":
        return PlainTextResponse("ok")

    # Telegram присылает JSON c Update
    try:
        data = await request.json()
    except Exception:
        return JSONResponse({"ok": False, "error": "invalid json"}, status_code=400)

    app = await ensure_app()

    # (необязательно) проверка секретного токена вебхука
    secret = os.getenv("TG_SECRET_TOKEN")
    if secret and request.headers.get("X-Telegram-Bot-Api-Secret-Token") != secret:
        return JSONResponse({"ok": False}, status_code=403)

    update = Update.de_json(data, app.bot)
    await app.process_update(update)
    return JSONResponse({"ok": True})

# Внутри Starlette маршрут — корень "/", снаружи Vercel добавит "/api/webhook"
app = Starlette(routes=[Route("/", webhook, methods=["GET", "POST"])])
