from starlette.applications import Starlette
from starlette.responses import PlainTextResponse
from starlette.routing import Route

async def ping(request):
    return PlainTextResponse("pong")

app = Starlette(routes=[Route("/", ping, methods=["GET"])])