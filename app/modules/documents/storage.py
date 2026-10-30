"""Bounded reads, detected file formats and private UUID-based storage keys."""

import asyncio
import hashlib
import os
from pathlib import Path
from uuid import uuid4

from app.core.config import settings
from app.core.errors import require

MAX_BYTES = 10 * 1024 * 1024


async def read_upload(file):
    content = await file.read(MAX_BYTES + 1)
    await file.close()
    require(
        0 < len(content) <= MAX_BYTES, "File must contain 1 byte to 10 MiB.", 413, "FILE_TOO_LARGE"
    )
    return content


def detect(content):
    from io import BytesIO

    if content.startswith(b"%PDF-"):
        from pypdf import PdfReader

        try:
            reader = PdfReader(BytesIO(content), strict=True)
            require(
                not reader.is_encrypted and len(reader.pages) > 0,
                "Encrypted or empty PDFs are unsupported.",
                415,
                "UNSUPPORTED_MEDIA",
            )
        except Exception:
            require(False, "Invalid PDF file.", 415, "UNSUPPORTED_MEDIA")
        return "application/pdf"
    from PIL import Image

    try:
        with Image.open(BytesIO(content)) as image:
            require(
                image.format in ("PNG", "JPEG") and image.width * image.height <= 40_000_000,
                "Image format or dimensions are unsupported.",
                415,
                "UNSUPPORTED_MEDIA",
            )
            media = "image/png" if image.format == "PNG" else "image/jpeg"
            image.verify()
            return media
    except Exception:
        require(
            False, "Only valid PDF, JPEG and PNG files are supported.", 415, "UNSUPPORTED_MEDIA"
        )


async def persist(ctx, content):
    media = await asyncio.to_thread(detect, content)
    key = uuid4().hex
    folder = Path(settings.private_upload_dir).resolve()
    path = folder / key

    def write():
        folder.mkdir(parents=True, exist_ok=True, mode=0o700)
        with path.open("xb") as f:
            os.chmod(path, 0o600)
            f.write(content)
            f.flush()
            os.fsync(f.fileno())

    await asyncio.to_thread(write)
    ctx.session.info.setdefault("new_files", []).append(path)
    return key, media, hashlib.sha256(content).hexdigest()


def content_path(key):
    require(
        len(key) == 32 and all(c in "0123456789abcdef" for c in key),
        "File is unavailable.",
        404,
        "NOT_FOUND",
    )
    path = Path(settings.private_upload_dir).resolve() / key
    require(path.is_file(), "File is unavailable.", 404, "NOT_FOUND")
    return path
