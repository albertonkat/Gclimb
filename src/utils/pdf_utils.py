"""
PDF utility functions: page counting, splitting large documents,
and basic quality assessment before sending to Claude.
"""
from __future__ import annotations

import io
import logging
from pathlib import Path
from typing import Iterator

logger = logging.getLogger(__name__)

MAX_PAGES_PER_CHUNK = 50      # Claude recommends splitting at 50 pages for best results
MAX_BYTES_PER_CHUNK = 28 * 1024 * 1024  # 28 MB (leave headroom under 32 MB limit)


def count_pages(pdf_bytes: bytes) -> int:
    """Quick page count using the PDF cross-reference table."""
    count = pdf_bytes.count(b"/Type /Page\n") + pdf_bytes.count(b"/Type/Page\n")
    return max(count, 1)


def split_pdf(pdf_bytes: bytes, max_pages: int = MAX_PAGES_PER_CHUNK) -> list[bytes]:
    """
    Split a large PDF into chunks of max_pages pages each.
    Requires pypdf (pip install pypdf).
    Falls back to returning the whole document if pypdf is not installed.
    """
    try:
        from pypdf import PdfReader, PdfWriter
    except ImportError:
        logger.warning("pypdf not installed — returning PDF as single chunk")
        return [pdf_bytes]

    reader = PdfReader(io.BytesIO(pdf_bytes))
    total = len(reader.pages)
    if total <= max_pages:
        return [pdf_bytes]

    chunks: list[bytes] = []
    for start in range(0, total, max_pages):
        writer = PdfWriter()
        for page in reader.pages[start : start + max_pages]:
            writer.add_page(page)
        buf = io.BytesIO()
        writer.write(buf)
        chunks.append(buf.getvalue())

    return chunks


def is_scanned(pdf_bytes: bytes) -> bool:
    """
    Heuristic: if a PDF has very little extractable text relative to its size,
    it is likely a scanned image (fax). This triggers the image-enhancement path.
    """
    text_bytes = pdf_bytes.count(b"BT") + pdf_bytes.count(b"ET")
    image_bytes = pdf_bytes.count(b"/Image")
    if text_bytes == 0 and image_bytes > 0:
        return True
    if image_bytes > 0 and text_bytes / max(image_bytes, 1) < 0.1:
        return True
    return False
