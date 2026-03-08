from fastapi import APIRouter

from src.api.v1 import router as v1_router
from src.config import settings

router = APIRouter(prefix=settings.app.api_prefix)
router.include_router(v1_router)

__all__ = ["router"]
