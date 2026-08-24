import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")


@dataclass(frozen=True)
class Settings:
    db_server: str = os.getenv("DB_SERVER", "localhost")
    db_name: str = os.getenv("DB_NAME", "")
    db_username: str = os.getenv("DB_USERNAME", "")
    db_password: str = os.getenv("DB_PASSWORD", "")
    db_driver: str = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")
    admin_username: str = os.getenv("ADMIN_USERNAME", "admin")
    admin_password: str = os.getenv("ADMIN_PASSWORD", "")
    allowed_origins: tuple[str, ...] = tuple(
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS", "http://localhost:4200,http://localhost:3000"
        ).split(",")
        if origin.strip()
    )
    media_directory: Path = BASE_DIR / "media"

    @property
    def connection_string(self) -> str:
        return (
            f"DRIVER={{{self.db_driver}}};"
            f"SERVER={self.db_server};"
            f"DATABASE={self.db_name};"
            f"UID={self.db_username};"
            f"PWD={self.db_password};"
            "Encrypt=no;TrustServerCertificate=yes;"
        )


settings = Settings()