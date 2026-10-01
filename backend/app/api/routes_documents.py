from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Document
from app.rag.ingest import chunk_text, extract_text
from app.rag.vector_store import add_chunks, delete_document
from app.schemas import DocumentUploadResponse

router = APIRouter(prefix="/documents", tags=["documents"])

ALLOWED_EXTENSIONS = (".pdf", ".docx", ".txt", ".md", ".csv")
MAX_SIZE_BYTES = 20 * 1024 * 1024  # 20 MB


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile, db: AsyncSession = Depends(get_db)) -> DocumentUploadResponse:
    if not file.filename.lower().endswith(ALLOWED_EXTENSIONS):
        raise HTTPException(400, f"Unsupported file type. Allowed: {ALLOWED_EXTENSIONS}")

    raw = await file.read()
    if len(raw) > MAX_SIZE_BYTES:
        raise HTTPException(400, "File exceeds 20 MB limit")

    text = extract_text(file.filename, raw)
    chunks = chunk_text(text)
    if not chunks:
        raise HTTPException(422, "No extractable text found in document")

    doc = Document(filename=file.filename, chunk_count=len(chunks))
    db.add(doc)
    await db.flush()

    add_chunks(doc.id, file.filename, chunks)
    await db.commit()

    return DocumentUploadResponse(id=doc.id, filename=doc.filename, chunk_count=doc.chunk_count)


@router.get("")
async def list_documents(db: AsyncSession = Depends(get_db)):
    rows = (await db.execute(select(Document))).scalars().all()
    return [{"id": d.id, "filename": d.filename, "chunk_count": d.chunk_count, "uploaded_at": d.uploaded_at} for d in rows]


@router.delete("/{doc_id}")
async def remove_document(doc_id: str, db: AsyncSession = Depends(get_db)):
    doc = await db.get(Document, doc_id)
    if not doc:
        raise HTTPException(404, "Document not found")
    delete_document(doc_id)
    await db.delete(doc)
    await db.commit()
    return {"status": "deleted"}
