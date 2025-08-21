import logging
from pathlib import Path
from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import TelegramError
from ..config import settings
from ..db_sqlite import Database
from ..logging_setup import event_log

logger = logging.getLogger("gatebot")

async def send_checklist(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database, source: str | None) -> None:
    root = Path(__file__).resolve().parents[2]
    pdf_path = root / "checklist.pdf"
    chat_id = update.effective_chat.id

    has_pdf = pdf_path.exists() and pdf_path.is_file() and pdf_path.stat().st_size > 0
    if has_pdf:
        try:
            await context.bot.send_document(
                chat_id=chat_id,
                document=pdf_path.open("rb"),
                caption="Checklist",
            )
        except TelegramError as e:
            logger.warning(f"Failed to send checklist.pdf, fallback to URL: {e!r}")
            await context.bot.send_message(chat_id=chat_id, text=settings.CHECKLIST_URL)
    else:
        await context.bot.send_message(chat_id=chat_id, text=settings.CHECKLIST_URL)

    await db.add_event(user_id=update.effective_user.id, event_type="sent_checklist", source=source)
    event_log(logger, "sent_checklist", update.effective_user.id, source, "Checklist sent")