from flask import Flask, request, jsonify
import os

app = Flask(__name__)

@app.route('/')
def index():
    return jsonify({
        "status": "ok",
        "message": "Telegram Bot API is running",
        "environment": os.getenv("VERCEL_ENV", "development"),
        "bot_token_set": bool(os.getenv("BOT_TOKEN")),
        "endpoints": ["/ping", "/webhook", "/test"]
    })

@app.route('/ping')
def ping():
    return jsonify({
        "status": "ok",
        "message": "pong",
        "environment": os.getenv("VERCEL_ENV", "development")
    })

@app.route('/test')
def test():
    return jsonify({
        "status": "ok",
        "message": "Test endpoint working",
        "environment": os.getenv("VERCEL_ENV", "development"),
        "bot_token_set": bool(os.getenv("BOT_TOKEN"))
    })

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        return "ok"
    
    # POST обработка будет добавлена позже
    return jsonify({"ok": True})

if __name__ == '__main__':
    app.run()
