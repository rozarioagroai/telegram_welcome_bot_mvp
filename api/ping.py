from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route('/')
def ping():
    return jsonify({
        "status": "ok",
        "message": "pong",
        "environment": os.getenv("VERCEL_ENV", "development"),
        "timestamp": "2025-08-19T20:30:00Z"
    })

if __name__ == '__main__':
    app.run()