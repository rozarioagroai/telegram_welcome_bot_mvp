# Простой webhook для диагностики
from http.server import BaseHTTPRequestHandler
import json
import os
import asyncio
import aiohttp

class handler(BaseHTTPRequestHandler):
    
    async def send_telegram_message(self, chat_id, text):
        """Отправляет сообщение в Telegram"""
        try:
            bot_token = os.getenv("BOT_TOKEN")
            if not bot_token:
                print("BOT_TOKEN not set")
                return
            
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            data = {
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "HTML"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data) as response:
                    if response.status == 200:
                        print(f"Message sent to {chat_id}: {text}")
                    else:
                        print(f"Failed to send message: {response.status}")
                        
        except Exception as e:
            print(f"Error sending message: {e}")
    def do_GET(self):
        """Health check endpoint"""
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b"ok")
        return
    
    def do_POST(self):
        """Простая обработка webhook от Telegram для диагностики"""
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
            
            # Парсим JSON от Telegram
            telegram_data = json.loads(post_data.decode('utf-8'))
            
            # Просто логируем полученные данные
            print(f"Received webhook data: {telegram_data}")
            
            # Простая обработка команд
            if 'message' in telegram_data and 'text' in telegram_data['message']:
                text = telegram_data['message']['text']
                chat_id = telegram_data['message']['chat']['id']
                
                if text == '/start':
                    # Отправляем приветственное сообщение
                    asyncio.run(self.send_telegram_message(chat_id, "Привет! Я бот для приветствия. Рад вас видеть! 🎉"))
                elif text == '/help':
                    asyncio.run(self.send_telegram_message(chat_id, "Доступные команды:\n/start - Начать\n/help - Помощь"))
                else:
                    asyncio.run(self.send_telegram_message(chat_id, f"Вы написали: {text}")
            
            # Возвращаем успех
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "ok": True, 
                "received": True,
                "message": "Webhook received and processed successfully",
                "data_type": type(telegram_data).__name__,
                "bot_token_set": bool(os.getenv("BOT_TOKEN"))
            }
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
