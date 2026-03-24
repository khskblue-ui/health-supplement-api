# health-supplement-api

건강기능식품 경쟁사 모니터링 백엔드 API

## 기술 스택

- Python 3.12
- FastAPI + Uvicorn
- SQLAlchemy 2.0 (async) + asyncpg
- Alembic (마이그레이션)
- APScheduler (일일 수집 스케줄)
- httpx (비동기 HTTP 클라이언트)
- PostgreSQL (Neon / Supabase 호환)

## 빠른 시작

```bash
# 의존성 설치
pip install -r requirements.txt

# 환경변수 설정
cp .env.example .env
# .env 파일에서 DATABASE_URL, FOOD_SAFETY_API_KEY 입력

# DB 마이그레이션 실행
alembic upgrade head

# 개발 서버 시작
uvicorn app.main:app --reload
```

## 환경변수

| 변수 | 설명 | 예시 |
|------|------|------|
| `DATABASE_URL` | PostgreSQL 연결 URL (asyncpg) | `postgresql+asyncpg://user:pass@host/db` |
| `FOOD_SAFETY_API_KEY` | 식품안전나라 공공 API 키 | `abc123...` |
| `CORS_ORIGINS` | 허용할 프론트엔드 오리진 (콤마 구분) | `http://localhost:3000` |
| `ENVIRONMENT` | 실행 환경 | `development` \| `production` |

## API 엔드포인트

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/health` | 헬스체크 |
| GET | `/api/dashboard/recent` | 4개사 최근 30일 신규 신고 요약 |
| GET | `/api/competitors` | 경쟁사 목록 + 총 품목 수 |
| GET | `/api/competitors/{id}` | 경쟁사 상세 + 12개월 추이 + 라이선스 |
| GET | `/api/competitors/{id}/registrations` | 월별/연도별 신고 품목 목록 |
| GET | `/api/analysis/production` | I0310 연간 생산량 비교 |

### 쿼리 파라미터

`GET /api/competitors/{id}/registrations`
- `period`: `monthly` | `yearly` (기본: `monthly`)
- `year`: 연도 (기본: 현재 연도)
- `month`: 월 (기본: 현재 월, period=monthly 시)
- `page`: 페이지 번호 (기본: 1)
- `size`: 페이지 크기 (기본: 50, 최대: 200)

`GET /api/analysis/production`
- `year`: 연도 (기본: 전년도)
- `competitor_id`: 경쟁사 ID 필터 (선택)

## 수집 API

| 서비스 | 설명 |
|--------|------|
| I0030 | 품목제조신고 |
| C003 | 품목제조신고 원재료 |
| I0320 | 이력추적관리 등록현황 |
| I0310 | 연간생산실적 |

## 스케줄

매일 **06:00 KST** (21:00 UTC) 자동 실행:
1. I0030 → `product_registrations` UPSERT
2. C003 → `raw_material_detail` 보완
3. I0320 → `traceability_registered` 업데이트
4. `collection_jobs` 이력 기록

## DB 마이그레이션

```bash
# 마이그레이션 적용
alembic upgrade head

# 롤백
alembic downgrade base
```

초기 마이그레이션(`001_initial_schema`)에는 다음이 포함됩니다:
- 전체 테이블 생성
- Materialized View 2개 (`mv_monthly_registrations`, `mv_yearly_registrations`)
- 경쟁사 4개사 시드 데이터
- 라이선스 플레이스홀더 시드 데이터

## Railway 배포

```
# Procfile에 정의됨
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Railway 환경변수에 `DATABASE_URL`, `FOOD_SAFETY_API_KEY`, `CORS_ORIGINS` 설정 후 배포.

## 대화형 API 문서

서버 실행 후 http://localhost:8000/docs 에서 Swagger UI 확인 가능.
