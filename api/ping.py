# Простая ping функция для Vercel
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
            "message": "pong",
            "environment": os.getenv("VERCEL_ENV", "development"),
            "timestamp": "2025-08-20T12:00:00Z"
        }
        
        self.wfile.write(json.dumps(response).encode())
        return
