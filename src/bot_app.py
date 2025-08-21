import sys
import asyncio

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import logging
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from .config import settings
from .logging_setup import setup_logging
from .db_sqlite import Database
from .handlers.start import start_handler
from .handlers.access import getaccess_handler
from .handlers.help import help_handler
from .handlers.callbacks import captcha_ok_handler, enter_data_handler
from .handlers.data import user_data_message_handler
from .services.throttling import Throttler
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from .handlers.admin_actions import admin_approve_handler, admin_deny_handler


logger = logging.getLogger("gatebot")

async def configure_channel_id(app: Application, db: Database) -> None:
    if settings.CHANNEL_ID is None and settings.CHANNEL_USERNAME:
        existing = await db.get_kv("CHANNEL_ID")
        if existing:
            return
        chat = await app.bot.get_chat(settings.CHANNEL_USERNAME)
        await db.set_kv("CHANNEL_ID", str(chat.id))
        logger.info(f"Resolved CHANNEL_ID={chat.id} from {settings.CHANNEL_USERNAME}")

async def post_init(app: Application) -> None:
    db = Database(settings.DB_PATH)
    await db.connect()
    await db.migrate()
    app.bot_data["db"] = db
    app.bot_data["throttler"] = Throttler()
    app.bot_data["captcha_deadlines"] = {}
    app.bot_data["awaiting_data"] = set()
    await configure_channel_id(app, db)

def build_app() -> Application:
    setup_logging()
    app = Application.builder().token(settings.BOT_TOKEN).post_init(post_init).build()

    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CallbackQueryHandler(captcha_ok_handler, pattern="^captcha_ok$"))
    app.add_handler(CallbackQueryHandler(enter_data_handler, pattern="^enter_data$"))
    app.add_handler(CallbackQueryHandler(admin_approve_handler, pattern=r"^admin_approve:\d+$"))
    app.add_handler(CallbackQueryHandler(admin_deny_handler, pattern=r"^admin_deny:\d+$"))
    app.add_handler(CommandHandler("getaccess", getaccess_handler))
    app.add_handler(CommandHandler("help", help_handler))
    app.add_handler(CommandHandler("enterdata", lambda u, c: enter_data_handler(u, c)))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, user_data_message_handler))

    return app

def main() -> None:
    app = build_app()
    if settings.USE_WEBHOOK:
        app.run_webhook(
            listen="0.0.0.0",
            port=settings.PORT,
            url_path="webhook",
            webhook_url=settings.WEBHOOK_URL,
        )
    else:
        app.run_polling()

if __name__ == "__main__":
    main()