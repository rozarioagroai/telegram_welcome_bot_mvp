import os, asyncio
from flask import Flask, request, jsonify
from telegram import Update
from src.bot_app import build_app

app = Flask(__name__)

_ptb_app = None

async def ensure_ptb_app():
    global _ptb_app
    if _ptb_app is None:
        _ptb_app = await build_app()
        await _ptb_app.initialize()
    return _ptb_app

@app.route('/', methods=['GET', 'POST'])
def webhook():
    # GET — удобный health-check
    if request.method == 'GET':
        return "ok"
    
    # POST — обработка webhook от Telegram
    try:
        data = request.get_json(force=True, silent=True) or {}
    except Exception:
        return jsonify({"ok": False, "error": "invalid json"}), 400

    # Проверка секретного токена вебхука
    secret = os.getenv("TG_SECRET_TOKEN")
    if secret and request.headers.get("X-Telegram-Bot-Api-Secret-Token") != secret:
        return jsonify({"ok": False}), 403

    # Обработка update
    try:
        ptb_app = asyncio.run(ensure_ptb_app())
        update = Update.de_json(data, ptb_app.bot)
        asyncio.run(ptb_app.process_update(update))
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run()
