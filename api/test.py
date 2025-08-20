from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route
import os

async def test(request):
    return JSONResponse({
        "status": "ok",
        "message": "Test endpoint working",
        "environment": os.getenv("VERCEL_ENV", "development"),
        "bot_token_set": bool(os.getenv("BOT_TOKEN")),
        "timestamp": "2025-08-19T20:30:00Z"
    })

app = Starlette(routes=[Route("/", test, methods=["GET"])])
