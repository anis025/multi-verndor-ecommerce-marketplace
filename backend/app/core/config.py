from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    APP_NAME: str = "Hatify"
    APP_ENV: str = "development"

    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "hatify_db"

    JWT_SECRET_KEY: str = "change-me-to-a-random-secret"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60

    FRONTEND_URL: str = "http://localhost:5173"

    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    EMAIL_FROM: str = ""
    SMTP_USE_SSL: bool = False
    SMTP_TIMEOUT: int = 10
    EMAIL_ENABLED: bool = True

    BRAND_NAME: str = "Hatify"
    BRAND_WEBSITE: str = "https://hatify.example.com"
    SUPPORT_EMAIL: str = "support@hatify.example.com"
    BRAND_LOGO_PATH: str = "static/hatify-logo.png"

    ADMIN_NAME: str = "Hatify Admin"
    ADMIN_EMAIL: str = "mdanis.dev@gmail.com"
    ADMIN_PASSWORD: str = "change-me"
    # The single email allowed to authenticate via the admin login endpoint.
    # Login is passwordless (email OTP). Set this to the email that should
    # be permitted to log in as admin. No other account can use the admin
    # login even if it has role=admin.
    ADMIN_ALLOWED_EMAIL: str = "mdanis.dev@gmail.com"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
