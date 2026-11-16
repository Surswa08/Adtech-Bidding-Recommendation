from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "adtech-bidding-system"
    redis_url: str = "redis://localhost:6379/0"
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_topic: str = "ad-events"
    attribution_window_hours: int = 168
    max_candidates: int = 100
    model_dir: str = "models"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
