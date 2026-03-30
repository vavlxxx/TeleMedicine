from __future__ import annotations

import asyncio
import hashlib
import sys
from pathlib import Path

from sqlalchemy import delete, func, insert, select

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.db import sessionmaker  # noqa: E402
from src.models.auth import RefreshSession, User  # noqa: E402
from src.models.doctor import DoctorQualificationDocument, Specialization, doctor_specializations  # noqa: E402
from src.models.enums import UserRole  # noqa: E402
from src.models.qa import Question, QuestionComment  # noqa: E402
from src.utils.files import ensure_upload_directory  # noqa: E402
from src.utils.security import create_refresh_token, generate_jti, hash_password, hash_token  # noqa: E402

SPECIALIZATION_NAMES = [
    "Cardiology",
    "Neurology",
    "Endocrinology",
    "Pediatrics",
    "Dermatology",
    "Gastroenterology",
    "Psychotherapy",
    "Pulmonology",
    "Rheumatology",
    "Otolaryngology",
    "Ophthalmology",
    "Nutrition",
]

ADMIN_USERS = [
    {
        "username": "seed_admin_01",
        "password": "SeedAdmin!123",
        "first_name": "Elena",
        "last_name": "Voronina",
        "role": UserRole.ADMIN,
    },
    {
        "username": "seed_admin_02",
        "password": "SeedAdmin!123",
        "first_name": "Maxim",
        "last_name": "Sorokin",
        "role": UserRole.ADMIN,
    },
]

PATIENT_USERS = [
    {"username": "seed_patient_01", "password": "SeedPatient!123", "first_name": "Ivan", "last_name": "Petrov"},
    {"username": "seed_patient_02", "password": "SeedPatient!123", "first_name": "Maria", "last_name": "Sokolova"},
    {"username": "seed_patient_03", "password": "SeedPatient!123", "first_name": "Alexey", "last_name": "Smirnov"},
    {"username": "seed_patient_04", "password": "SeedPatient!123", "first_name": "Olga", "last_name": "Kuznetsova"},
    {"username": "seed_patient_05", "password": "SeedPatient!123", "first_name": "Daria", "last_name": "Fedorova"},
    {"username": "seed_patient_06", "password": "SeedPatient!123", "first_name": "Pavel", "last_name": "Romanov"},
    {"username": "seed_patient_07", "password": "SeedPatient!123", "first_name": "Nikita", "last_name": "Belov"},
    {"username": "seed_patient_08", "password": "SeedPatient!123", "first_name": "Irina", "last_name": "Morozova"},
    {"username": "seed_patient_09", "password": "SeedPatient!123", "first_name": "Tatyana", "last_name": "Volkova"},
    {"username": "seed_patient_10", "password": "SeedPatient!123", "first_name": "Denis", "last_name": "Popov"},
    {"username": "seed_patient_11", "password": "SeedPatient!123", "first_name": "Vera", "last_name": "Orlova"},
    {"username": "seed_patient_12", "password": "SeedPatient!123", "first_name": "Roman", "last_name": "Gusev"},
]

DOCTOR_USERS = [
    {
        "username": "seed_doctor_01",
        "password": "SeedDoctor!123",
        "first_name": "Anna",
        "last_name": "Lebedeva",
        "specializations": ["Cardiology", "Nutrition"],
        "is_verified_doctor": True,
    },
    {
        "username": "seed_doctor_02",
        "password": "SeedDoctor!123",
        "first_name": "Sergey",
        "last_name": "Karpov",
        "specializations": ["Neurology", "Psychotherapy"],
        "is_verified_doctor": True,
    },
    {
        "username": "seed_doctor_03",
        "password": "SeedDoctor!123",
        "first_name": "Polina",
        "last_name": "Nikitina",
        "specializations": ["Endocrinology", "Nutrition"],
        "is_verified_doctor": True,
    },
    {
        "username": "seed_doctor_04",
        "password": "SeedDoctor!123",
        "first_name": "Igor",
        "last_name": "Romanenko",
        "specializations": ["Pediatrics", "Otolaryngology"],
        "is_verified_doctor": True,
    },
    {
        "username": "seed_doctor_05",
        "password": "SeedDoctor!123",
        "first_name": "Natalia",
        "last_name": "Abramova",
        "specializations": ["Dermatology", "Ophthalmology"],
        "is_verified_doctor": True,
    },
    {
        "username": "seed_doctor_06",
        "password": "SeedDoctor!123",
        "first_name": "Artem",
        "last_name": "Mikhailov",
        "specializations": ["Gastroenterology", "Nutrition"],
        "is_verified_doctor": True,
    },
    {
        "username": "seed_doctor_07",
        "password": "SeedDoctor!123",
        "first_name": "Ekaterina",
        "last_name": "Komarova",
        "specializations": ["Psychotherapy", "Neurology"],
        "is_verified_doctor": True,
    },
    {
        "username": "seed_doctor_08",
        "password": "SeedDoctor!123",
        "first_name": "Mikhail",
        "last_name": "Tarasov",
        "specializations": ["Pulmonology", "Cardiology"],
        "is_verified_doctor": True,
    },
    {
        "username": "seed_doctor_09",
        "password": "SeedDoctor!123",
        "first_name": "Yulia",
        "last_name": "Solovyova",
        "specializations": ["Rheumatology", "Endocrinology"],
        "is_verified_doctor": True,
    },
    {
        "username": "seed_doctor_10",
        "password": "SeedDoctor!123",
        "first_name": "Kirill",
        "last_name": "Anisimov",
        "specializations": ["Otolaryngology", "Pediatrics"],
        "is_verified_doctor": True,
    },
    {
        "username": "seed_doctor_11",
        "password": "SeedDoctor!123",
        "first_name": "Svetlana",
        "last_name": "Ermakova",
        "specializations": ["Ophthalmology", "Dermatology"],
        "is_verified_doctor": False,
    },
    {
        "username": "seed_doctor_12",
        "password": "SeedDoctor!123",
        "first_name": "Viktor",
        "last_name": "Loginov",
        "specializations": ["Nutrition", "Gastroenterology"],
        "is_verified_doctor": False,
    },
]

QUESTION_TOPICS = [
    "persistent headache and dizziness for five days",
    "dry cough that becomes worse at night",
    "blood sugar readings keep climbing in the morning",
    "rash on hands after household chemicals",
    "stomach pain after meals and bloating",
    "child has fever and sore throat since yesterday",
    "shortness of breath while climbing stairs",
    "ankle pain and swelling after a long walk",
    "red eyes after several hours at the computer",
    "ringing in ears after a recent cold",
    "fatigue and low appetite for two weeks",
    "skin peeling on elbows and knees",
]

ANSWER_TEMPLATES = [
    "Please book an in-person appointment, keep a symptom diary, and complete baseline blood tests.",
    "Increase hydration, avoid self-medication for now, and arrange a focused specialist consultation.",
    "The symptoms warrant a targeted examination and a review of current medications within the next few days.",
    "Until you are seen, monitor temperature, pulse, and triggers, then share the notes with the clinician.",
]


def build_pdf_bytes(title: str) -> bytes:
    return (
        "%PDF-1.4\n"
        "1 0 obj\n"
        "<< /Type /Catalog /Pages 2 0 R >>\n"
        "endobj\n"
        "2 0 obj\n"
        "<< /Type /Pages /Count 1 /Kids [3 0 R] >>\n"
        "endobj\n"
        "3 0 obj\n"
        "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 200 200] >>\n"
        "endobj\n"
        f"% {title}\n"
        "trailer\n"
        "<< /Root 1 0 R >>\n"
        "%%EOF\n"
    ).encode("utf-8")


async def upsert_specialization(session, name: str) -> Specialization:
    specialization = await session.scalar(select(Specialization).where(Specialization.name == name))
    if specialization is None:
        specialization = Specialization(name=name)
        session.add(specialization)
        await session.flush()
    return specialization


async def upsert_user(
    session,
    *,
    username: str,
    password: str,
    role: UserRole,
    first_name: str,
    last_name: str,
    is_verified_doctor: bool = False,
) -> User:
    user = await session.scalar(select(User).where(User.username == username))
    if user is None:
        user = User(
            username=username,
            password_hash=hash_password(password),
            first_name=first_name,
            last_name=last_name,
            role=role,
            is_active=True,
            is_verified_doctor=is_verified_doctor,
        )
        session.add(user)
        await session.flush()
        return user

    user.password_hash = hash_password(password)
    user.first_name = first_name
    user.last_name = last_name
    user.role = role
    user.is_active = True
    user.is_verified_doctor = is_verified_doctor
    await session.flush()
    return user


async def ensure_doctor_documents(session, doctor: User) -> None:
    upload_dir = ensure_upload_directory()

    for index in range(1, 3):
        original_file_name = f"{doctor.username}_document_{index}.pdf"
        stored_file_name = f"{doctor.username}_document_{index}.pdf"
        content = build_pdf_bytes(f"{doctor.username}-document-{index}")
        file_path = upload_dir / stored_file_name
        file_path.write_bytes(content)

        sha256 = hashlib.sha256(content).hexdigest()
        document = await session.scalar(
            select(DoctorQualificationDocument).where(DoctorQualificationDocument.stored_file_name == stored_file_name)
        )
        if document is None:
            session.add(
                DoctorQualificationDocument(
                    doctor_id=doctor.id,
                    original_file_name=original_file_name,
                    stored_file_name=stored_file_name,
                    content_type="application/pdf",
                    size_bytes=len(content),
                    sha256=sha256,
                )
            )
            continue

        document.doctor_id = doctor.id
        document.original_file_name = original_file_name
        document.content_type = "application/pdf"
        document.size_bytes = len(content)
        document.sha256 = sha256


async def sync_doctor_specializations(session, doctor: User, specialization_ids: list[int]) -> None:
    await session.execute(delete(doctor_specializations).where(doctor_specializations.c.doctor_id == doctor.id))
    await session.execute(
        insert(doctor_specializations),
        [{"doctor_id": doctor.id, "specialization_id": specialization_id} for specialization_id in specialization_ids],
    )


async def ensure_refresh_session(session, user: User) -> None:
    active_session = await session.scalar(
        select(RefreshSession).where(
            RefreshSession.user_id == user.id,
            RefreshSession.revoked_at.is_(None),
        )
    )
    if active_session is not None:
        return

    jti = generate_jti()
    refresh_token, expires_at = create_refresh_token(user.id, jti)
    session.add(
        RefreshSession(
            jti=jti,
            user_id=user.id,
            token_hash=hash_token(refresh_token),
            user_agent="seed-script/1.0",
            ip_address="127.0.0.1",
            expires_at=expires_at,
        )
    )


async def upsert_question(session, author: User, text: str) -> Question:
    question = await session.scalar(select(Question).where(Question.text == text))
    if question is None:
        question = Question(text=text, author_id=author.id)
        session.add(question)
        await session.flush()
        return question

    question.author_id = author.id
    await session.flush()
    return question


async def ensure_comment(session, question: Question, author: User, text: str) -> None:
    comment = await session.scalar(
        select(QuestionComment).where(
            QuestionComment.question_id == question.id,
            QuestionComment.author_id == author.id,
            QuestionComment.text == text,
        )
    )
    if comment is None:
        session.add(
            QuestionComment(
                question_id=question.id,
                author_id=author.id,
                text=text,
            )
        )


async def main() -> None:
    ensure_upload_directory()

    async with sessionmaker() as session:
        specializations = {}
        for name in SPECIALIZATION_NAMES:
            specializations[name] = await upsert_specialization(session, name)
        await session.commit()

        admins: list[User] = []
        patients: list[User] = []
        doctors: list[User] = []

        for payload in ADMIN_USERS:
            admins.append(
                await upsert_user(
                    session,
                    username=payload["username"],
                    password=payload["password"],
                    role=payload["role"],
                    first_name=payload["first_name"],
                    last_name=payload["last_name"],
                )
            )

        for payload in PATIENT_USERS:
            patients.append(
                await upsert_user(
                    session,
                    username=payload["username"],
                    password=payload["password"],
                    role=UserRole.PATIENT,
                    first_name=payload["first_name"],
                    last_name=payload["last_name"],
                )
            )

        for payload in DOCTOR_USERS:
            doctor = await upsert_user(
                session,
                username=payload["username"],
                password=payload["password"],
                role=UserRole.DOCTOR,
                first_name=payload["first_name"],
                last_name=payload["last_name"],
                is_verified_doctor=payload["is_verified_doctor"],
            )
            await sync_doctor_specializations(
                session,
                doctor,
                [specializations[name].id for name in payload["specializations"]],
            )
            await ensure_doctor_documents(session, doctor)
            doctors.append(doctor)

        await session.commit()

        for user in [*admins, *patients, *doctors]:
            await ensure_refresh_session(session, user)
        await session.commit()

        verified_doctors = [doctor for doctor in doctors if doctor.is_verified_doctor]
        for index, patient in enumerate(patients):
            for offset in range(2):
                topic = QUESTION_TOPICS[(index + offset) % len(QUESTION_TOPICS)]
                question_text = f"[seed-q-{index * 2 + offset + 1:02d}] I need advice about {topic}."
                question = await upsert_question(session, patient, question_text)

                doctor = verified_doctors[(index + offset) % len(verified_doctors)]
                answer_text = (
                    f"[seed-a-{index * 2 + offset + 1:02d}] "
                    f"{ANSWER_TEMPLATES[(index + offset) % len(ANSWER_TEMPLATES)]}"
                )
                await ensure_comment(session, question, doctor, answer_text)

        await session.commit()

        counts = {
            "users": int(await session.scalar(select(func.count(User.id))) or 0),
            "specializations": int(await session.scalar(select(func.count(Specialization.id))) or 0),
            "documents": int(await session.scalar(select(func.count(DoctorQualificationDocument.id))) or 0),
            "refresh_sessions": int(await session.scalar(select(func.count(RefreshSession.id))) or 0),
            "questions": int(await session.scalar(select(func.count(Question.id))) or 0),
            "question_comments": int(await session.scalar(select(func.count(QuestionComment.id))) or 0),
        }

    print("Seed completed:")
    for key, value in counts.items():
        print(f"  {key}: {value}")
    print("Credentials:")
    print("  admin: seed_admin_01 / SeedAdmin!123")
    print("  patient: seed_patient_01 / SeedPatient!123")
    print("  doctor: seed_doctor_01 / SeedDoctor!123")


if __name__ == "__main__":
    asyncio.run(main())
