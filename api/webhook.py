# Простой webhook для диагностики
from http.server import BaseHTTPRequestHandler
import json
import os

class handler(BaseHTTPRequestHandler):
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
            
            # Возвращаем успех
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "ok": True, 
                "received": True,
                "message": "Webhook received successfully",
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
