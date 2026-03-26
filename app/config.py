from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List
import os


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://user:pass@localhost/health_supplement"

    # Food Safety Korea API
    # I0030/C003/I0310: 공공데이터포털(data.go.kr)에서 별도 신청
    FOOD_SAFETY_API_KEY: str = ""
    # I0320 전용 키 (식품이력추적관리 등록현황) - 현재 보유
    FOOD_SAFETY_API_KEY_I0320: str = ""

    # CORS
    CORS_ORIGINS: str = "http://localhost:3000"

    # Environment
    ENVIRONMENT: str = "development"

    # App
    APP_TITLE: str = "Health Supplement Competitor Monitor API"
    APP_VERSION: str = "1.0.0"

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


settings = Settings()
