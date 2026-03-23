# Sample Search Server

FastAPI server for storing documents and running simple ranked text search.

## Run

```bash
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8002
```

Docs: http://localhost:8002/docs

## Health

- GET /health

## Key Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | /health | Service health check |
| POST | /documents | Create document |
| GET | /documents | List documents with pagination |
| GET | /documents/{document_id} | Get document by id |
| DELETE | /documents/{document_id} | Delete document |
| GET | /search?q=... | Search title, content, and tags |

## Quick Example

```bash
curl -X POST http://localhost:8002/documents \
  -H "Content-Type: application/json" \
  -d '{"title":"FastAPI Guide","content":"Build backend APIs quickly","tags":["python","api"]}'

curl "http://localhost:8002/search?q=api"
```

## Notes

- Search ranking is score-based and intentionally simple for demo use.
- Data is in memory and resets on restart.
