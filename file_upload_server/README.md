# Sample File Upload Server

FastAPI server for file upload, metadata lookup, download, and delete operations.

## Run

```bash
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8001
```

Docs: http://localhost:8001/docs

## Health

- GET /health

## Key Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | /health | Service health check |
| POST | /files/upload | Upload multipart file using field file |
| GET | /files | List file metadata |
| GET | /files/{file_id} | Get single file metadata |
| GET | /files/{file_id}/download | Download file by id |
| DELETE | /files/{file_id} | Delete file by id |

## Quick Example

```bash
curl -X POST http://localhost:8001/files/upload \
  -F "file=@/path/to/image.png"
```

## Notes

- Uploaded files are stored in local uploads directory.
- Metadata is stored in memory and resets on restart.
