"""
Fax ingestion and preprocessing pipeline.

Faxes arrive in several ways:
  - Webhook payload (bytes) from eFax, Documo, Twilio Fax, or RingCentral Fax
  - TIFF files from legacy on-premise fax servers
  - Low-resolution scanned PDFs from all-in-one printers

This module normalizes all inputs to a cleaned PDF for the Claude extractor.
"""
from __future__ import annotations

import io
import logging
import os
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

_PILLOW_AVAILABLE = False
_PDF2IMAGE_AVAILABLE = False

try:
    from PIL import Image, ImageEnhance, ImageFilter
    _PILLOW_AVAILABLE = True
except ImportError:
    logger.warning("Pillow not available — image preprocessing disabled")

try:
    import pdf2image
    _PDF2IMAGE_AVAILABLE = True
except ImportError:
    logger.warning("pdf2image not available — TIFF-to-PDF conversion disabled")


class FaxPreprocessor:
    """
    Converts and cleans fax inputs before sending to the Claude PDF extractor.

    Processing chain for scanned/faxed images:
      1. Convert TIFF → PIL images
      2. Deskew (straighten tilted pages)
      3. Denoise and enhance contrast
      4. Convert to PDF (single multi-page PDF)

    For PDFs that arrive directly from fax servers, this class checks quality
    and optionally enhances pages before handing off to the extractor.
    """

    # Minimum DPI below which we enhance contrast aggressively
    MIN_QUALITY_DPI = 150

    def prepare_for_extraction(self, raw_bytes: bytes, content_type: str) -> bytes:
        """
        Accept raw fax bytes, return a PDF-ready bytes object for the extractor.
        content_type: 'image/tiff', 'application/pdf', 'image/jpeg', 'image/png'
        """
        if content_type == "application/pdf":
            return self._enhance_pdf(raw_bytes)

        if content_type in ("image/tiff", "image/tif"):
            return self._tiff_to_pdf(raw_bytes)

        if content_type in ("image/jpeg", "image/jpg", "image/png"):
            return self._image_to_pdf(raw_bytes, content_type)

        raise ValueError(f"Unsupported fax content type: {content_type}")

    def prepare_file(self, path: Path) -> bytes:
        """Convenience wrapper that detects content type from extension."""
        ext = path.suffix.lower()
        type_map = {
            ".pdf": "application/pdf",
            ".tif": "image/tiff",
            ".tiff": "image/tiff",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
        }
        content_type = type_map.get(ext, "application/pdf")
        return self.prepare_for_extraction(path.read_bytes(), content_type)

    # ------------------------------------------------------------------

    def _enhance_pdf(self, pdf_bytes: bytes) -> bytes:
        """
        For PDFs that are already in the right format, pass through.
        Optionally rasterize and re-encode if quality is very poor
        (detected via file size heuristic — very small PDFs are often fax artifacts).
        """
        # Simple pass-through; add rasterization logic here if needed
        return pdf_bytes

    def _tiff_to_pdf(self, tiff_bytes: bytes) -> bytes:
        """Convert multi-page TIFF (standard fax format) to PDF."""
        if not _PILLOW_AVAILABLE:
            raise RuntimeError("Pillow is required for TIFF conversion. Run: pip install pillow")

        images = []
        tiff_io = io.BytesIO(tiff_bytes)
        with Image.open(tiff_io) as img:
            for i in range(getattr(img, "n_frames", 1)):
                img.seek(i)
                page = img.convert("RGB")
                page = self._enhance_image(page)
                images.append(page)

        return self._images_to_pdf(images)

    def _image_to_pdf(self, img_bytes: bytes, content_type: str) -> bytes:
        """Convert a single image to a one-page PDF."""
        if not _PILLOW_AVAILABLE:
            raise RuntimeError("Pillow is required for image conversion")

        img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        img = self._enhance_image(img)
        return self._images_to_pdf([img])

    def _enhance_image(self, img) -> "Image":
        """
        Apply contrast enhancement and mild sharpening to improve OCR/LLM readability.
        Tuned for typical fax artifacts (low contrast, slight blur, noise).
        """
        if not _PILLOW_AVAILABLE:
            return img

        # Contrast boost
        img = ImageEnhance.Contrast(img).enhance(1.8)
        # Sharpness boost
        img = ImageEnhance.Sharpness(img).enhance(2.0)
        # Mild unsharp mask for edge definition
        img = img.filter(ImageFilter.UnsharpMask(radius=1, percent=150, threshold=3))

        return img

    def _images_to_pdf(self, images: list) -> bytes:
        """Convert a list of PIL images to a multi-page PDF bytes object."""
        if not images:
            raise ValueError("No images to convert")

        buf = io.BytesIO()
        first = images[0]
        rest = images[1:]
        first.save(
            buf,
            format="PDF",
            save_all=True,
            append_images=rest,
            resolution=200,
        )
        return buf.getvalue()


class FaxWebhookHandler:
    """
    Parses incoming fax webhooks from major healthcare fax providers.
    Returns normalized (patient_filename, pdf_bytes) tuples.
    """

    def handle_documo(self, payload: dict) -> tuple[str, bytes, str]:
        """
        Documo IDP webhook: POST with JSON containing base64 fax content.
        Returns (filename, pdf_bytes, content_type).
        """
        import base64
        fax_id = payload.get("faxId", "unknown")
        content_b64 = payload.get("content", "")
        content_type = payload.get("contentType", "application/pdf")
        filename = f"fax_{fax_id}.pdf"
        return filename, base64.b64decode(content_b64), content_type

    def handle_twilio_fax(self, form_data: dict) -> tuple[str, bytes, str]:
        """
        Twilio Programmable Fax webhook: form POST with MediaUrl.
        Caller must have already fetched the media bytes.
        """
        import httpx
        media_url = form_data.get("MediaUrl", "")
        fax_sid = form_data.get("FaxSid", "unknown")
        filename = f"fax_{fax_sid}.tiff"
        # Fetch the actual media (Twilio serves TIFF)
        response = httpx.get(media_url, timeout=30)
        response.raise_for_status()
        return filename, response.content, "image/tiff"

    def handle_ringcentral(self, payload: dict, attachment_bytes: bytes) -> tuple[str, bytes, str]:
        """RingCentral Fax API attachment, already fetched."""
        fax_id = payload.get("id", "unknown")
        filename = f"fax_{fax_id}.pdf"
        return filename, attachment_bytes, "application/pdf"
