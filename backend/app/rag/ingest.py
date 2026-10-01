"""Parse uploaded documents (PDF, DOCX, TXT/MD, CSV headers) into overlapping
text chunks suitable for embedding."""

from __future__ import annotations

import io

import pypdf
from docx import Document as DocxDocument


def extract_text(filename: str, raw: bytes) -> str:
    lower = filename.lower()
    if lower.endswith(".pdf"):
        reader = pypdf.PdfReader(io.BytesIO(raw))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    if lower.endswith(".docx"):
        doc = DocxDocument(io.BytesIO(raw))
        return "\n".join(p.text for p in doc.paragraphs)
    # Fallback: treat as plain text (txt, md, csv, log)
    return raw.decode("utf-8", errors="ignore")


def chunk_text(text: str, chunk_size: int = 900, overlap: int = 150) -> list[str]:
    """Simple sliding-window chunker on whitespace-normalized text."""
    text = " ".join(text.split())
    if not text:
        return []
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        if end == len(text):
            break
        start = end - overlap
    return chunks
