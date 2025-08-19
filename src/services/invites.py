import time
from datetime import datetime, timedelta
from telegram import Bot
from telegram.error import TelegramError
from ..db import Database

async def create_one_time_invite(
    bot: Bot,
    db: Database,
    chat_id: int,
    ttl_seconds: int,
    user_id: int,
) -> str:
    expire_at_dt = datetime.utcnow() + timedelta(seconds=ttl_seconds)
    try:
        link = await bot.create_chat_invite_link(
            chat_id=chat_id,
            expire_date=expire_at_dt,
            member_limit=1,
            name=f"user_{user_id}_{int(time.time())}",
        )
    except TelegramError as e:
        raise
    await db.save_invite(user_id=user_id, link=link.invite_link, expire_at=int(expire_at_dt.timestamp()))
    return link.invite_link