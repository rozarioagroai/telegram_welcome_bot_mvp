from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    BOT_TOKEN: str
    CHANNEL_ID: int | None = None
    CHANNEL_USERNAME: str | None = None

    INVITE_TTL_SECONDS: int = 86400
    CAPTCHA_TTL_SECONDS: int = 60
    START_THROTTLE_SECONDS: int = 10
    GETACCESS_THROTTLE_SECONDS: int = 15

    REF_BASE_URL: str = "https://example.com/ref"
    UTM_CAMPAIGN: str = "first_trade"

    CHECKLIST_URL: str
    LOG_LEVEL: str = "INFO"

    USE_WEBHOOK: bool = False
    WEBHOOK_URL: str | None = None
    PORT: int = 8000

    DB_PATH: str = Field(default="bot.db")
    DATABASE_URL: str | None = None

    # NEW: comma/semicolon separated list of admin user_ids
    ADMIN_IDS: list[int] = Field(default_factory=list)

    @field_validator("ADMIN_IDS", mode="before")
    @classmethod
    def _parse_admin_ids(cls, v):
        if v is None or v == "":
            return []
        if isinstance(v, list):
            return [int(x) for x in v]
        raw = str(v).replace(";", ",")
        return [int(x.strip()) for x in raw.split(",") if x.strip().isdigit()]

settings = Settings()