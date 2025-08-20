# Webhook функция для Telegram
from http.server import BaseHTTPRequestHandler
import json
import os

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b"ok")
        return
    
    def do_POST(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        # Читаем данные от Telegram
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            # Парсим JSON от Telegram
            telegram_data = json.loads(post_data.decode('utf-8'))
            
            # Пока просто возвращаем успех
            response = {"ok": True, "received": True}
            self.wfile.write(json.dumps(response).encode())
        except Exception as e:
            response = {"ok": False, "error": str(e)}
            self.wfile.write(json.dumps(response).encode())
        
        return
