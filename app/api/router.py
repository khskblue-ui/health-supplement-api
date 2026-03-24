from fastapi import APIRouter
from app.api import dashboard, competitors, registrations, analysis

api_router = APIRouter(prefix="/api")

api_router.include_router(dashboard.router, tags=["dashboard"])
api_router.include_router(competitors.router, tags=["competitors"])
api_router.include_router(registrations.router, tags=["registrations"])
api_router.include_router(analysis.router, tags=["analysis"])
