import os
from dotenv import load_dotenv

# 加载项目根目录下 .env 环境变量文件
_env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))
if os.path.exists(_env_path):
    load_dotenv(_env_path)
else:
    load_dotenv()

_bootstrap_key: str = ""

def _get_or_create_bootstrap_key() -> str:
    global _bootstrap_key
    if not _bootstrap_key:
        import secrets
        _bootstrap_key = "ac_boot_" + secrets.token_urlsafe(24)
    return _bootstrap_key


class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "Agent Control Plane")
    APP_ENV: str = os.getenv("APP_ENV", "development")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    PORT: int = int(os.getenv("PORT", "8000"))
    # 安全加固：默认监听本地回环地址 127.0.0.1，避免无防护直接暴露到公网 0.0.0.0
    HOST: str = os.getenv("HOST", "127.0.0.1")

    # 安全与身份认证 (CWE-306 防御)
    API_KEY: str = os.getenv("API_KEY") or os.getenv("AGENT_CONTROL_API_KEY") or ""
    REQUIRE_AUTH: bool = os.getenv("REQUIRE_AUTH", "true").lower() == "true"
    CORS_ORIGINS: list[str] = [
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:8000,http://127.0.0.1:8000,http://localhost:5173,http://127.0.0.1:5173"
        ).split(",")
        if origin.strip()
    ]

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
    def effective_api_key(self) -> str:
        """获取当前生效的 API 密钥，若未配置则生成内存态临时引导密钥"""
        if self.API_KEY:
            return self.API_KEY
        return _get_or_create_bootstrap_key()

    @property
    def sync_database_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        pwd = f":{self.DB_PASSWORD}" if self.DB_PASSWORD else ""
        return f"mysql+pymysql://{self.DB_USER}{pwd}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"

settings = Settings()

