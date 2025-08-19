import argparse
import asyncio
from telegram import Bot
from ..config import settings
from ..db import Database

async def resolve_and_store_channel_id(channel_username: str) -> int:
    bot = Bot(token=settings.BOT_TOKEN)
    chat = await bot.get_chat(channel_username)
    channel_id = chat.id
    db = Database(settings.DB_PATH)
    await db.connect()
    try:
        await db.migrate()
        await db.set_kv("CHANNEL_ID", str(channel_id))
    finally:
        await db.close()
    print(channel_id)
    return channel_id

def main():
    parser = argparse.ArgumentParser(description="Resolve channel id by @username and store in kv")
    parser.add_argument("--channel", required=True, help="@username of the channel")
    args = parser.parse_args()
    asyncio.run(resolve_and_store_channel_id(args.channel))

if __name__ == "__main__":
    main()