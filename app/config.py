from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List
from pathlib import Path

# 프로젝트 루트 (app/config.py 기준 상위 디렉토리)
_PROJECT_ROOT = Path(__file__).parent.parent


class Settings(BaseSettings):
    # Database (로컬 개발: SQLite, 프로덕션: PostgreSQL URL로 교체)
    DATABASE_URL: str = f"sqlite+aiosqlite:///{_PROJECT_ROOT}/health_supplement.db"

    # Food Safety Korea API
    # I0030/C003/I0310: 공공데이터포털(data.go.kr)에서 별도 신청
    FOOD_SAFETY_API_KEY: str = ""
    # I0320 전용 키 (식품이력추적관리 등록현황) - 현재 보유
    FOOD_SAFETY_API_KEY_I0320: str = ""

    # CORS (쉼표 구분 목록 또는 "*")
    CORS_ORIGINS: str = "*"

    # Environment
    ENVIRONMENT: str = "development"

    # App
    APP_TITLE: str = "Health Supplement Competitor Monitor API"
    APP_VERSION: str = "1.0.0"

    @field_validator('DATABASE_URL', mode='before')
    @classmethod
    def fix_database_url(cls, v: str) -> str:
        import sys
        if not v:
            print("[DB-DEBUG] DATABASE_URL is empty, using default", file=sys.stderr)
            return v
        # Log scheme and query string (no password)
        scheme = v.split('://')[0] if '://' in v else 'unknown'
        query_raw = v.split('?', 1)[1] if '?' in v else '(none)'
        print(f"[DB-DEBUG] scheme={scheme!r} query={query_raw!r}", file=sys.stderr)

        if v.startswith('postgresql://'):
            v = v.replace('postgresql://', 'postgresql+asyncpg://', 1)
        elif v.startswith('postgres://'):
            v = v.replace('postgres://', 'postgresql+asyncpg://', 1)
        # asyncpg does not accept sslmode — strip it from the URL
        if '?' in v:
            base, query = v.split('?', 1)
            params = [p for p in query.split('&') if not p.startswith('sslmode=')]
            v = base + ('?' + '&'.join(params) if params else '')
        print(f"[DB-DEBUG] final scheme={v.split('://')[0]!r} has_sslmode={'sslmode=' in v}", file=sys.stderr)
        return v

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


settings = Settings()
