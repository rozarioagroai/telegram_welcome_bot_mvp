# api/index.py
import os, json, asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import Application

BOT_TOKEN = os.environ["BOT_TOKEN"]
# Собираем PTB-приложение один раз на «холодный старт» функции
ptb_app = Application.builder().token(BOT_TOKEN).build()

app = Flask(__name__)

@app.post("https://tgbotgate.vercel.app/api/webhook")  # итоговый URL: https://<project>.vercel.app/api/webhook
def webhook():
    data = request.get_json(force=True, silent=True) or {}
    update = Update.de_json(data, ptb_app.bot)
    # Выполняем обработку апдейта синхронно в рамках запроса
    asyncio.run(ptb_app.initialize())
    asyncio.run(ptb_app.process_update(update))
    asyncio.run(ptb_app.shutdown())
    return {"ok": True}
