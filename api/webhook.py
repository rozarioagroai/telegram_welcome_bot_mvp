# Webhook функция для Telegram с полной интеграцией
from http.server import BaseHTTPRequestHandler
import json
import os
import asyncio

# Глобальная переменная для хранения экземпляра бота
_ptb_app = None

async def ensure_ptb_app():
    """Инициализирует и возвращает экземпляр PTB приложения"""
    global _ptb_app
    if _ptb_app is None:
        try:
            # Импортируем здесь, чтобы избежать проблем с путями
            from telegram.ext import Application
            from telegram import Bot
            
            bot_token = os.getenv("BOT_TOKEN")
            if not bot_token:
                raise ValueError("BOT_TOKEN not set")
            
            # Создаем простое приложение для обработки updates
            bot = Bot(token=bot_token)
            _ptb_app = Application.builder().token(bot_token).build()
            await _ptb_app.initialize()
            print("PTB app initialized successfully")
        except Exception as e:
            print(f"Error initializing PTB app: {e}")
            raise
    return _ptb_app

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Health check endpoint"""
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b"ok")
        return
    
    def do_POST(self):
        """Обработка webhook от Telegram"""
        try:
            # Читаем данные от Telegram
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {"ok": False, "error": "No content"}
                self.wfile.write(json.dumps(response).encode())
                return
            
            post_data = self.rfile.read(content_length)
            
            # Проверяем секретный токен (если установлен)
            secret = os.getenv("TG_SECRET_TOKEN")
            if secret and self.headers.get("X-Telegram-Bot-Api-Secret-Token") != secret:
                self.send_response(403)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {"ok": False, "error": "Invalid secret token"}
                self.wfile.write(json.dumps(response).encode())
                return
            
            # Парсим JSON от Telegram
            telegram_data = json.loads(post_data.decode('utf-8'))
            
            # Создаем Update объект
            from telegram import Update
            ptb_app = asyncio.run(ensure_ptb_app())
            update = Update.de_json(telegram_data, ptb_app.bot)
            
            # Обрабатываем update
            asyncio.run(ptb_app.process_update(update))
            
            # Возвращаем успех
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"ok": True, "processed": True}
            self.wfile.write(json.dumps(response).encode())
            
        except json.JSONDecodeError as e:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"ok": False, "error": f"Invalid JSON: {str(e)}"}
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"ok": False, "error": str(e)}
            self.wfile.write(json.dumps(response).encode())
            print(f"Error processing webhook: {e}")
        
        return
