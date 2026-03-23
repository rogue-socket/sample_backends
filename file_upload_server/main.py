from datetime import UTC, datetime
from pathlib import Path
import shutil
import uuid

from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel

app = FastAPI(title="Sample File Upload Server")

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# In-memory metadata store: {file_id: metadata}
FILES: dict[str, dict] = {}


class FileMetadata(BaseModel):
    id: str
    original_name: str
    stored_name: str
    content_type: str
    size_bytes: int
    uploaded_at: str


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "file_upload"}


@app.post("/files/upload", response_model=FileMetadata)
def upload_file(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="File must have a filename")

    file_id = uuid.uuid4().hex
    suffix = Path(file.filename).suffix
    stored_name = f"{file_id}{suffix}"
    destination = UPLOAD_DIR / stored_name

    with destination.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    size_bytes = destination.stat().st_size
    metadata = {
        "id": file_id,
        "original_name": file.filename,
        "stored_name": stored_name,
        "content_type": file.content_type or "application/octet-stream",
        "size_bytes": size_bytes,
        "uploaded_at": datetime.now(UTC).isoformat(),
        "path": str(destination),
    }
    FILES[file_id] = metadata

    return FileMetadata(**metadata)


@app.get("/files")
def list_files(
    filename: str | None = Query(None, description="Filter by original filename contains"),
    content_type: str | None = Query(None, description="Filter by exact content type"),
):
    records = list(FILES.values())

    if filename:
        needle = filename.lower()
        records = [record for record in records if needle in record["original_name"].lower()]

    if content_type:
        records = [record for record in records if record["content_type"] == content_type]

    return {
        "total": len(records),
        "files": [
            {
                "id": record["id"],
                "original_name": record["original_name"],
                "content_type": record["content_type"],
                "size_bytes": record["size_bytes"],
                "uploaded_at": record["uploaded_at"],
            }
            for record in records
        ],
    }


@app.get("/files/{file_id}")
def get_file_metadata(file_id: str):
    record = FILES.get(file_id)
    if record is None:
        raise HTTPException(status_code=404, detail="File not found")

    return {
        "id": record["id"],
        "original_name": record["original_name"],
        "stored_name": record["stored_name"],
        "content_type": record["content_type"],
        "size_bytes": record["size_bytes"],
        "uploaded_at": record["uploaded_at"],
    }


@app.get("/files/{file_id}/download")
def download_file(file_id: str):
    record = FILES.get(file_id)
    if record is None:
        raise HTTPException(status_code=404, detail="File not found")

    path = Path(record["path"])
    if not path.exists():
        raise HTTPException(status_code=404, detail="Stored file is missing on disk")

    return FileResponse(path=str(path), media_type=record["content_type"], filename=record["original_name"])


@app.delete("/files/{file_id}")
def delete_file(file_id: str):
    record = FILES.pop(file_id, None)
    if record is None:
        raise HTTPException(status_code=404, detail="File not found")

    path = Path(record["path"])
    if path.exists():
        path.unlink()

    return {"status": "deleted", "file_id": file_id}
