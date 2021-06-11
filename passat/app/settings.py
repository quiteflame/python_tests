from pydantic import BaseSettings


class Settings(BaseSettings):
    secret_key: str
    sqlalchemy_url: str = "sqlite:///./db.sqlite3"
    access_token_expire_minutes: int = 60 * 24 * 8  # 60 minutes * 24 hours * 8 days = 8 days
    super_user_email: str
    super_user_password: str

    class Config:
        env_file = ".env"


settings = Settings()

if settings.super_user_password is None:
    settings.super_user_password = settings.secret_key
