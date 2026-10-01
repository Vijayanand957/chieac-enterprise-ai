"""Retrieval agent: answers questions grounded in uploaded organizational
documents using RAG over the vector store."""
from app.agents.llm_client import complete
from app.rag.vector_store import similarity_search

SYSTEM_PROMPT = """You are the Retrieval Agent in an enterprise AI operations
assistant. You answer questions using ONLY the provided document excerpts.
If the excerpts don't contain the answer, say so plainly instead of guessing.
Cite the source filename in parentheses after each claim."""


def run(query: str, k: int = 5) -> dict:
    hits = similarity_search(query, k=k)
    if not hits:
        return {
            "answer": "No relevant documents are indexed yet. Upload documents to enable retrieval.",
            "sources": [],
        }

    context = "\n\n".join(f"[{h['filename']}]: {h['text']}" for h in hits)
    user_prompt = f"Document excerpts:\n{context}\n\nQuestion: {query}"
    answer = complete(SYSTEM_PROMPT, user_prompt)
    sources = sorted({h["filename"] for h in hits})
    return {"answer": answer, "sources": sources}
