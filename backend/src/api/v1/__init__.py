from fastapi import APIRouter

from src.api.v1.admin import router as admin_router
from src.api.v1.auth import router as auth_router
from src.api.v1.doctor import router as doctor_router
from src.api.v1.maintenance import router as maintenance_router
from src.api.v1.qa import router as qa_router
from src.api.v1.specializations import router as specializations_router
from src.config import settings

router = APIRouter(prefix=settings.app.v1_prefix)
router.include_router(auth_router)
router.include_router(admin_router)
router.include_router(maintenance_router)
router.include_router(specializations_router)
router.include_router(doctor_router)
router.include_router(qa_router)

__all__ = ["router"]
