from fastapi import HTTPException, UploadFile, status
from sqlalchemy.exc import IntegrityError

from src.api.v1.serializers import to_doctor_list_item, to_document_dto
from src.config import settings
from src.models.auth import User
from src.models.doctor import DoctorQualificationDocument
from src.models.enums import UserRole
from src.repos.loaders import DOCTOR_DIRECTORY_OPTIONS
from src.schemas.doctor import DoctorListItemDTO, DoctorQualificationDocumentDTO
from src.services.base import BaseService
from src.utils.files import save_doctor_document


def _cleanup_files(file_names: list[str]) -> None:
    for file_name in file_names:
        (settings.upload.directory / file_name).unlink(missing_ok=True)


class DoctorService(BaseService):
    async def list_doctors(self, specialization_id: int | None, offset: int, limit: int) -> list[DoctorListItemDTO]:
        doctors = await self.db.users.list_public_doctors(specialization_id, offset, limit, *DOCTOR_DIRECTORY_OPTIONS)
        return [to_doctor_list_item(item) for item in doctors]

    async def get_doctor(self, doctor_id: int) -> DoctorListItemDTO:
        doctor = await self.db.users.get_public_doctor_by_id(doctor_id, *DOCTOR_DIRECTORY_OPTIONS)
        if doctor is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found")
        return to_doctor_list_item(doctor)

    async def upload_my_documents(
        self,
        current_user: User,
        documents: list[UploadFile],
    ) -> list[DoctorQualificationDocumentDTO]:
        if current_user.role != UserRole.DOCTOR:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only doctors can upload qualification documents")
        if not documents:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No files uploaded")
        if len(documents) > settings.upload.max_files_per_request:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Maximum {settings.upload.max_files_per_request} files per request",
            )

        saved_file_names: list[str] = []
        try:
            for upload in documents:
                file_meta = await save_doctor_document(upload)
                saved_file_names.append(file_meta.stored_file_name)
                self.db.documents.add(
                    DoctorQualificationDocument(
                        doctor_id=current_user.id,
                        original_file_name=file_meta.original_file_name,
                        stored_file_name=file_meta.stored_file_name,
                        content_type=file_meta.content_type,
                        size_bytes=file_meta.size_bytes,
                        sha256=file_meta.sha256,
                    )
                )

            await self.db.commit()
        except IntegrityError as exc:
            await self.db.rollback()
            _cleanup_files(saved_file_names)
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Duplicate document") from exc
        except Exception:
            await self.db.rollback()
            _cleanup_files(saved_file_names)
            raise

        documents_list = await self.db.documents.list_by_doctor(current_user.id)
        return [to_document_dto(item) for item in documents_list]
