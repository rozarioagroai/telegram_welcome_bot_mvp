import asyncio
from telegram import Update
from src.bot_app import build_app

_app = None
_loop = asyncio.new_event_loop()
asyncio.set_event_loop(_loop)

async def _ensure_app():
    global _app
    if _app is None:
        _app = await build_app()  # создаёт Application, post_init подключит Neon
        await _app.initialize()
    return _app

def handler(request):
    if request.method != "POST":
        return ("OK", 200)
    data = request.get_json(force=True, silent=True) or {}
    async def _process():
        app = await _ensure_app()
        update = Update.de_json(data, app.bot)
        await app.process_update(update)
        return "OK"
    return (_loop.run_until_complete(_process()), 200)