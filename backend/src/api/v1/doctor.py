from fastapi import APIRouter, File, Query, UploadFile, status

from src.api.v1.dependencies.auth import CurrentUserDep
from src.api.v1.dependencies.db import DBDep
from src.schemas.doctor import DoctorListItemDTO, DoctorQualificationDocumentDTO
from src.services.doctor import DoctorService

router = APIRouter(prefix="/doctors", tags=["Doctors"])


@router.get("/", response_model=list[DoctorListItemDTO])
async def list_doctors(
    db: DBDep,
    specialization_id: int | None = Query(default=None, ge=1),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
) -> list[DoctorListItemDTO]:
    return await DoctorService(db).list_doctors(specialization_id=specialization_id, offset=offset, limit=limit)


@router.get("/{doctor_id}", response_model=DoctorListItemDTO)
async def get_doctor(doctor_id: int, db: DBDep) -> DoctorListItemDTO:
    return await DoctorService(db).get_doctor(doctor_id)


@router.post("/me/documents", response_model=list[DoctorQualificationDocumentDTO], status_code=status.HTTP_201_CREATED)
async def upload_my_documents(
    db: DBDep,
    current_user: CurrentUserDep,
    documents: list[UploadFile] = File(...),
) -> list[DoctorQualificationDocumentDTO]:
    return await DoctorService(db).upload_my_documents(current_user=current_user, documents=documents)
