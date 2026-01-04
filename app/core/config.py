from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )

    APP_NAME: str = "Ghayamathia API"
    ENV: str = "production"


    # Format attendu :
    # postgresql+psycopg2://USER:PASSWORD@HOST/DB?sslmode=require
    DATABASE_URL: str

    JWT_SECRET: str
    JWT_ALG: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 heures

    ADMIN_EMAIL: str = "admin@ghayamathia.com"
    ADMIN_PASSWORD: str = "ChangeMeStrongPassword!"


settings = Settings()
