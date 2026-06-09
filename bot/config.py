from pydantic_settings import BaseSettings, SettingsConfigDict


class BotSettings(BaseSettings):
    TELEGRAM_TOKEN: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


bot_settings = BotSettings()
