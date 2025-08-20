from starlette.applications import Starlette
from starlette.responses import PlainTextResponse, JSONResponse
from starlette.routing import Route
import os

async def ping(request):
    # Добавляем больше информации для диагностики
    return JSONResponse({
        "status": "ok",
        "message": "pong",
        "environment": os.getenv("VERCEL_ENV", "development"),
        "timestamp": "2025-08-19T20:30:00Z"
    })

app = Starlette(routes=[Route("/", ping, methods=["GET"])])