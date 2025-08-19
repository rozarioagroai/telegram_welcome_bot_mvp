import logging
from .config import settings

def setup_logging() -> None:
    logging.basicConfig(
        format="[%(levelname)s] %(asctime)s %(message)s",
        level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    )

def event_log(logger: logging.Logger, event: str, user_id: int | None, source: str | None, message: str) -> None:
    parts = [message, f"event={event}"]
    if user_id is not None:
        parts.append(f"user_id={user_id}")
    if source:
        parts.append(f"source={source}")
    logger.info(" ".join(parts))