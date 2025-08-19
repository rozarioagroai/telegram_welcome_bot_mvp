import asyncio
from starlette.applications import Starlette
from starlette.responses import PlainTextResponse
from starlette.routing import Route
from starlette.requests import Request
from telegram import Update
from src.bot_app import build_app

_app = None
_loop = asyncio.get_event_loop_policy().new_event_loop()

async def ensure_app():
    global _app
    if _app is None:
        _app = await build_app()
        await _app.initialize()
    return _app

async def webhook(request: Request):
    if request.method != "POST":
        return PlainTextResponse("OK")
    data = await request.json()
    app = await ensure_app()
    update = Update.de_json(data, app.bot)
    await app.process_update(update)
    return PlainTextResponse("OK")

app = Starlette(routes=[Route("/", webhook, methods=["GET", "POST"])])