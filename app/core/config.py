import os

class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "Agent Control Plane")
    APP_ENV: str = os.getenv("APP_ENV", "development")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    PORT: int = int(os.getenv("PORT", "8000"))
    HOST: str = os.getenv("HOST", "0.0.0.0")

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    DB_HOST: str = os.getenv("DB_HOST", "127.0.0.1")
    DB_PORT: int = int(os.getenv("DB_PORT", "13306"))
    DB_USER: str = os.getenv("DB_USER", "root")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    DB_NAME: str = os.getenv("DB_NAME", "agent_control")
    DB_ECHO: bool = os.getenv("DB_ECHO", "false").lower() == "true"

    DEFAULT_TASK_LEASE_SECONDS: int = int(os.getenv("DEFAULT_TASK_LEASE_SECONDS", "300"))
    HEARTBEAT_THRESHOLD_SECONDS: int = int(os.getenv("HEARTBEAT_THRESHOLD_SECONDS", "60"))

    @property
    def sync_database_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        pwd = f":{self.DB_PASSWORD}" if self.DB_PASSWORD else ""
        return f"mysql+pymysql://{self.DB_USER}{pwd}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"

settings = Settings()
