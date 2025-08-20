# Максимально простая функция для Vercel
from http.server import BaseHTTPRequestHandler
import json
import os

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response = {
            "status": "ok",
            "message": "Telegram Bot API is working!",
            "environment": os.getenv("VERCEL_ENV", "development"),
            "bot_token_set": bool(os.getenv("BOT_TOKEN")),
            "path": self.path
        }
        
        self.wfile.write(json.dumps(response).encode())
        return
    
    def do_POST(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response = {"ok": True, "message": "POST received"}
        self.wfile.write(json.dumps(response).encode())
        return
