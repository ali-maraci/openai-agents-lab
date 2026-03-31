import os


class Settings:
    def __init__(self):
        self.db_path: str = os.getenv("DB_PATH", "sessions.db")
        self.session_expiry_days: int = int(os.getenv("SESSION_EXPIRY_DAYS", "5"))


settings = Settings()
