import asyncio
import logging
from io import BytesIO

import google.generativeai as genai
import pdfplumber
from PyPDF2 import PdfReader

from app.core.config import settings
from app.domain.documents.exceptions import DocumentPipelineError
from app.domain.documents.schemas import PDFExtractionResult

logger = logging.getLogger(__name__)


class PDFProcessor:
    def __init__(self, scanned_text_threshold: int | None = None) -> None:
        self.scanned_text_threshold = scanned_text_threshold or settings.scanned_text_threshold

    async def process(self, pdf_bytes: bytes, filename: str) -> PDFExtractionResult:
        try:
            extraction = await asyncio.to_thread(self._extract_with_pdfplumber, pdf_bytes)
            method = "pdfplumber"
        except DocumentPipelineError:
            logger.warning("pdfplumber_failed_using_pypdf2_fallback", extra={"document_filename": filename})
            extraction = await asyncio.to_thread(self._extract_with_pypdf2, pdf_bytes)
            method = "pypdf2"

        if not extraction["document_text"].strip():
            extraction = await asyncio.to_thread(self._extract_with_pypdf2, pdf_bytes)
            method = "pypdf2"

        is_scanned = self._is_scanned(extraction["document_text"], extraction["page_count"])
        if is_scanned:
            if settings.gemini_api_key:
                logger.info("scanned_pdf_detected_using_gemini_ocr", extra={"document_filename": filename})
                ocr_text = await self._extract_with_gemini_vision(pdf_bytes, filename)
                return PDFExtractionResult(
                    document_text=ocr_text,
                    page_count=extraction["page_count"],
                    extraction_method="gemini_vision_ocr",
                    page_texts=[ocr_text],
                    is_scanned=True,
                )

            logger.warning("scanned_pdf_detected_without_gemini_key", extra={"document_filename": filename})
            method = f"{method}_scanned_no_ocr_configured"

        return PDFExtractionResult(
            document_text=extraction["document_text"],
            page_count=extraction["page_count"],
            extraction_method=method,
            page_texts=extraction["page_texts"],
            is_scanned=is_scanned,
        )

    def _extract_with_pdfplumber(self, pdf_bytes: bytes) -> dict[str, object]:
        page_texts: list[str] = []
        try:
            with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
                for page in pdf.pages:
                    page_texts.append(page.extract_text() or "")
                return {
                    "document_text": "\n\n".join(page_texts).strip(),
                    "page_count": len(pdf.pages),
                    "page_texts": page_texts,
                }
        except Exception as exc:
            logger.exception("pdfplumber_extraction_failed")
            raise DocumentPipelineError(f"pdfplumber extraction failed: {exc}") from exc

    def _extract_with_pypdf2(self, pdf_bytes: bytes) -> dict[str, object]:
        try:
            reader = PdfReader(BytesIO(pdf_bytes))
            page_texts = [(page.extract_text() or "") for page in reader.pages]
            return {
                "document_text": "\n\n".join(page_texts).strip(),
                "page_count": len(reader.pages),
                "page_texts": page_texts,
            }
        except Exception as exc:
            logger.exception("pypdf2_extraction_failed")
            raise DocumentPipelineError(f"PyPDF2 extraction failed: {exc}") from exc

    def _is_scanned(self, document_text: str, page_count: int) -> bool:
        if page_count <= 0:
            return True
        return len(document_text.strip()) < self.scanned_text_threshold * page_count

    async def _extract_with_gemini_vision(self, pdf_bytes: bytes, filename: str) -> str:
        def run_ocr() -> str:
            genai.configure(api_key=settings.gemini_api_key)
            model = genai.GenerativeModel(settings.gemini_model)
            response = model.generate_content(
                [
                    "Extract all readable text from this industrial PDF. Preserve page order, headings, tables, equipment identifiers, dates, and incident descriptions.",
                    {"mime_type": "application/pdf", "data": pdf_bytes},
                ],
                generation_config={"temperature": 0},
            )
            return response.text or ""

        try:
            text = await asyncio.to_thread(run_ocr)
        except Exception as exc:
            logger.exception("gemini_vision_ocr_failed", extra={"document_filename": filename})
            raise DocumentPipelineError(f"Gemini Vision OCR failed for {filename}: {exc}") from exc

        if not text.strip():
            raise DocumentPipelineError(f"Gemini Vision OCR returned no text for {filename}")
        return text.strip()
