from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route('/')
def test():
    return jsonify({
        "status": "ok",
        "message": "Test endpoint working",
        "environment": os.getenv("VERCEL_ENV", "development"),
        "bot_token_set": bool(os.getenv("BOT_TOKEN")),
        "timestamp": "2025-08-19T20:30:00Z"
    })

if __name__ == '__main__':
    app.run()
