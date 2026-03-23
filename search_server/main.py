from datetime import UTC, datetime
import uuid

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

app = FastAPI(title="Sample Search Server")

# In-memory document store: {document_id: document}
DOCUMENTS: dict[str, dict] = {}


class DocumentCreate(BaseModel):
    title: str = Field(min_length=1)
    content: str = Field(min_length=1)
    tags: list[str] = Field(default_factory=list)


class Document(DocumentCreate):
    id: str
    created_at: str


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "search"}


@app.post("/documents", response_model=Document)
def create_document(payload: DocumentCreate):
    doc_id = uuid.uuid4().hex
    document = {
        "id": doc_id,
        "title": payload.title,
        "content": payload.content,
        "tags": payload.tags,
        "created_at": datetime.now(UTC).isoformat(),
    }
    DOCUMENTS[doc_id] = document
    return Document(**document)


@app.get("/documents")
def list_documents(limit: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0)):
    docs = list(DOCUMENTS.values())
    sliced = docs[offset: offset + limit]
    return {
        "total": len(docs),
        "offset": offset,
        "limit": limit,
        "documents": sliced,
    }


@app.get("/documents/{document_id}", response_model=Document)
def get_document(document_id: str):
    document = DOCUMENTS.get(document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return Document(**document)


@app.delete("/documents/{document_id}")
def delete_document(document_id: str):
    deleted = DOCUMENTS.pop(document_id, None)
    if deleted is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"status": "deleted", "document_id": document_id}


@app.get("/search")
def search_documents(
    q: str = Query(..., min_length=1, description="Search query"),
    tag: str | None = Query(None, description="Optional tag filter"),
    limit: int = Query(10, ge=1, le=50),
):
    query = q.lower().strip()
    results: list[dict] = []

    for document in DOCUMENTS.values():
        title = document["title"].lower()
        content = document["content"].lower()
        tags = [value.lower() for value in document["tags"]]

        if tag and tag.lower() not in tags:
            continue

        title_hits = title.count(query)
        content_hits = content.count(query)
        if title_hits == 0 and content_hits == 0 and query not in tags:
            continue

        score = (title_hits * 3) + content_hits + (2 if query in tags else 0)
        results.append(
            {
                "id": document["id"],
                "title": document["title"],
                "tags": document["tags"],
                "score": score,
                "created_at": document["created_at"],
            }
        )

    results.sort(key=lambda item: item["score"], reverse=True)

    return {
        "query": q,
        "tag": tag,
        "total": len(results),
        "results": results[:limit],
    }
