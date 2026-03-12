from sqlalchemy import select

from src.models.doctor import DoctorQualificationDocument
from src.repos.base import BaseRepo


class DoctorDocumentRepo(BaseRepo):
    def add(self, document: DoctorQualificationDocument) -> None:
        self.session.add(document)

    async def get_by_id(self, document_id: int) -> DoctorQualificationDocument | None:
        statement = select(DoctorQualificationDocument).where(DoctorQualificationDocument.id == document_id)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def list_by_doctor(self, doctor_id: int) -> list[DoctorQualificationDocument]:
        statement = (
            select(DoctorQualificationDocument)
            .where(DoctorQualificationDocument.doctor_id == doctor_id)
            .order_by(DoctorQualificationDocument.created_at.desc())
        )
        result = await self.session.execute(statement)
        return list(result.scalars().all())
