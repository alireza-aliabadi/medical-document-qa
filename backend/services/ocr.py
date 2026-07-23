"""OCR and text extraction from PDF documents."""

import io
import logging
from dataclasses import dataclass

import pdfplumber
from pypdf import PdfReader

logger = logging.getLogger(__name__)


@dataclass
class PageText:
    page_number: int
    text: str


@dataclass
class ExtractedDocument:
    pages: list[PageText]
    metadata: dict[str, str | int | None]

    @property
    def full_text(self) -> str:
        return "\n\n".join(page.text for page in self.pages if page.text.strip())


class OCRService:
    """Extract text from PDFs. Uses pdfplumber with pypdf fallback."""

    def extract(self, pdf_bytes: bytes, filename: str) -> ExtractedDocument:
        pages: list[PageText] = []
        metadata: dict[str, str | int | None] = {"filename": filename}

        try:
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                metadata["page_count"] = len(pdf.pages)
                for idx, page in enumerate(pdf.pages, start=1):
                    text = page.extract_text() or ""
                    pages.append(PageText(page_number=idx, text=text.strip()))
        except Exception as exc:
            logger.warning("pdfplumber failed, falling back to pypdf: %s", exc)
            reader = PdfReader(io.BytesIO(pdf_bytes))
            metadata["page_count"] = len(reader.pages)
            for idx, pdf_page in enumerate(reader.pages, start=1):
                text = pdf_page.extract_text() or ""
                pages.append(PageText(page_number=idx, text=text.strip()))

        if not any(p.text for p in pages):
            logger.info("No text layer found in %s; OCR would run in production", filename)
            metadata["ocr_required"] = True

        return ExtractedDocument(pages=pages, metadata=metadata)
