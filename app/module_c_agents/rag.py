from sqlalchemy import select
from google.genai import types

from app.db import SessionLocal
from app.models import KnowledgeDoc
from app.module_b_triage.llm_client import _client


def embed(text: str) -> list[float]:
    resp = _client.models.embed_content(
        model="text-embedding-004",
        contents=[text],
        config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT"),
    )
    return resp.embeddings[0].values


def add_document(title: str, content: str) -> None:
    with SessionLocal() as session:
        session.add(KnowledgeDoc(title=title, content=content, embedding=embed(content)))
        session.commit()


def retrieve(query: str, k: int = 4) -> list[str]:
    qvec = embed(query)
    with SessionLocal() as session:
        docs = session.scalars(
            select(KnowledgeDoc).order_by(KnowledgeDoc.embedding.cosine_distance(qvec)).limit(k)
        ).all()
        return [f"{d.title}: {d.content}" for d in docs]