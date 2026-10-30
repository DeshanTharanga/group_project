"""Printed-text OCR. Untrusted text is returned for human review, never auto-prescribed."""

import subprocess
import tempfile
from pathlib import Path


class OCRError(Exception):
    def __init__(self, code):
        self.code = code


def extract_text(path, media):
    try:
        if media == "application/pdf":
            from pypdf import PdfReader

            reader = PdfReader(path)
            if len(reader.pages) > 20:
                raise OCRError("OCR_PAGE_LIMIT")
            text = "\n".join((page.extract_text() or "") for page in reader.pages)
            if text.strip():
                return text[:32000]
            with tempfile.TemporaryDirectory() as tmp:
                subprocess.run(
                    [
                        "pdftoppm",
                        "-f",
                        "1",
                        "-l",
                        "20",
                        "-scale-to",
                        "1800",
                        "-png",
                        str(path),
                        str(Path(tmp) / "page"),
                    ],
                    check=True,
                    timeout=60,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                return "\n".join(_image_text(p) for p in sorted(Path(tmp).glob("page-*.png")))[
                    :32000
                ]
        return _image_text(path)[:32000]
    except FileNotFoundError as exc:
        raise OCRError("OCR_ENGINE_UNAVAILABLE") from exc
    except (subprocess.SubprocessError, ValueError) as exc:
        raise OCRError("OCR_EXTRACTION_FAILED") from exc


def _image_text(path):
    result = subprocess.run(
        ["tesseract", str(path), "stdout", "-l", "eng", "--psm", "6"],
        check=True,
        timeout=45,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    return result.stdout.decode("utf-8", errors="replace")
