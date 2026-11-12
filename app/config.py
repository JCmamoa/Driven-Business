from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://aiops:aiops@localhost:5432/aiops"
    rabbitmq_url: str = "amqp://aiops:aiops@localhost:5672/"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"
    refund_human_approval_threshold: float = 200.0
    log_level: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()