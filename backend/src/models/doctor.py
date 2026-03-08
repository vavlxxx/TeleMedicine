from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Column, ForeignKey, Integer, String, Table, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base

if TYPE_CHECKING:
    from src.models.auth import User


doctor_specializations = Table(
    "doctor_specializations",
    Base.metadata,
    Column("doctor_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("specialization_id", Integer, ForeignKey("specializations.id", ondelete="CASCADE"), primary_key=True),
)


class Specialization(Base):
    __tablename__ = "specializations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, index=True)

    doctors: Mapped[list[User]] = relationship(
        secondary=doctor_specializations,
        back_populates="specializations",
    )


class DoctorQualificationDocument(Base):
    __tablename__ = "doctor_qualification_documents"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    doctor_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    original_file_name: Mapped[str] = mapped_column(String(255))
    stored_file_name: Mapped[str] = mapped_column(String(255), unique=True)
    content_type: Mapped[str] = mapped_column(String(100))
    size_bytes: Mapped[int] = mapped_column(BigInteger)
    sha256: Mapped[str] = mapped_column(String(64))

    doctor: Mapped[User] = relationship(back_populates="qualification_documents")

    __table_args__ = (
        UniqueConstraint("doctor_id", "sha256", name="uq_doctor_document_sha256"),
    )
