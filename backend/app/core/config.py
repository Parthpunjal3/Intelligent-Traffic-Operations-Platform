"""
Application configuration, loaded from environment variables (.env).
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    PROJECT_NAME: str = "Smart City Traffic AI"
    API_V1_PREFIX: str = "/api/v1"

    # Database
    POSTGRES_USER: str = "traffic_admin"
    POSTGRES_PASSWORD: str = "changeme"
    POSTGRES_DB: str = "traffic_db"
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    # Congestion thresholds (vehicles per lane per minute)
    CONGESTION_MODERATE_THRESHOLD: int = 15
    CONGESTION_HEAVY_THRESHOLD: int = 30

    # Forecast horizon in minutes
    FORECAST_HORIZON_MIN: int = 30
    FORECAST_INTERVAL_MIN: int = 5

    # CV model
    YOLO_MODEL_PATH: str = "yolov8n.pt"
    DETECTION_CONFIDENCE: float = 0.4

    SECRET_KEY: str = "change-this-secret-key"


settings = Settings()
