from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "ThreatShield 5G"
    ENVIRONMENT: str = "development"
    DATABASE_URL: str = "sqlite:///./threatshield.db"
    SECRET_KEY: str = "CHANGE_ME_IN_PRODUCTION"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    DATASET_PATH: str = "data/sample/5g_nidd_sample.csv"
    MODEL_DIR: str = "models"
    ALERT_THRESHOLD: float = 0.70
    FRONTEND_URL: str = "http://localhost:5173"
    DEMO_MODE: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
