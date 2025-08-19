from telegram import Update
from telegram.ext import ContextTypes

HELP_TEXT = (
    "Hi! Use /start to begin. After KYC/registration via the link, use /getaccess to receive a one-time invite.\n"
    "Если капча истекла, повторите /start. Для доступа после регистрации — /getaccess."
)

async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(HELP_TEXT)