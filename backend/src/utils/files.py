from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status

from src.config import settings


@dataclass
class StoredFileMeta:
    original_file_name: str
    stored_file_name: str
    content_type: str
    size_bytes: int
    sha256: str


def ensure_upload_directory() -> Path:
    settings.upload.directory.mkdir(parents=True, exist_ok=True)
    return settings.upload.directory


async def save_doctor_document(upload_file: UploadFile) -> StoredFileMeta:
    upload_dir = ensure_upload_directory()

    if not upload_file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file has no filename")

    original_name = Path(upload_file.filename).name
    extension = Path(original_name).suffix.lower().lstrip(".")
    if extension not in settings.upload.allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file extension: .{extension}",
        )

    content_type = (upload_file.content_type or "application/octet-stream").lower()
    if content_type not in settings.upload.allowed_mime_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported content type: {content_type}",
        )

    stored_file_name = f"{uuid4().hex}.{extension}"
    destination = upload_dir / stored_file_name

    max_size_bytes = settings.upload.max_file_size_mb * 1024 * 1024
    size_bytes = 0
    digest = hashlib.sha256()

    try:
        with destination.open("wb") as target:
            while True:
                chunk = await upload_file.read(1024 * 1024)
                if not chunk:
                    break
                size_bytes += len(chunk)
                if size_bytes > max_size_bytes:
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=f"File exceeds {settings.upload.max_file_size_mb} MB limit",
                    )
                digest.update(chunk)
                target.write(chunk)
    except Exception:
        destination.unlink(missing_ok=True)
        raise
    finally:
        await upload_file.close()

    if size_bytes == 0:
        destination.unlink(missing_ok=True)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empty files are not allowed")

    return StoredFileMeta(
        original_file_name=original_name,
        stored_file_name=stored_file_name,
        content_type=content_type,
        size_bytes=size_bytes,
        sha256=digest.hexdigest(),
    )


def resolve_document_path(stored_file_name: str) -> Path:
    file_name = Path(stored_file_name).name
    path = settings.upload.directory / file_name
    if not path.exists() or not path.is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document file not found")
    return path
