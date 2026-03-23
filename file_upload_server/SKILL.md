---
name: File Upload Server
description: File management API with upload, download, metadata, and filtering capabilities.
port: 8001
tech: FastAPI
---

# File Upload Server Skill

FastAPI-based file management service running on port 8001. Handles file uploads, downloads, filtering, and metadata tracking with persistent disk storage.

## Overview

**Purpose:** Provide a standalone file storage and retrieval service. Stores files on disk in ./uploads/ directory with in-memory metadata. Supports filtering, listing, and lifecycle management.

**When to Use:**
- Building document management or file sharing features
- Testing file upload UI components
- Integrating file storage into larger applications
- Testing attachment workflows

**Base URL:** http://localhost:8001

**Storage:** Files persisted in ./uploads/ directory relative to server

## Setup Verification

```bash
# Check service is running
curl -s http://localhost:8001/files | jq '.total'

# Expected: 0 (no files initially) or existing file count
```

## Core Workflows with Examples

### 1. Upload a File

**Request:**
```bash
curl -X POST http://localhost:8001/files/upload \
  -F "file=@/path/to/document.pdf" \
  -F "description=Q2 Report" \
  -F "tags=finance,quarterly"
```

**Response:**
```json
{
  "id": "file_550e8400e29b",
  "filename": "document.pdf",
  "size_bytes": 245187,
  "mime_type": "application/pdf",
  "description": "Q2 Report",
  "tags": ["finance", "quarterly"],
  "uploaded_at": "2026-03-24T10:30:45Z"
}
```

**Multiple files:**
```bash
curl -X POST http://localhost:8001/files/upload \
  -F "file=@report.pdf" \
  -F "file=@spreadsheet.xlsx" \
  -F "tags=documents"
```

### 2. List Files with Filtering

**Get all files:**
```bash
curl "http://localhost:8001/files"
```

**Filter by tag:**
```bash
curl "http://localhost:8001/files?tags=finance"
```

**Search by filename:**
```bash
curl "http://localhost:8001/files?search=report"
```

**Combined filters:**
```bash
curl "http://localhost:8001/files?tags=finance&mime_type=application/pdf&skip=10&limit=5"
```

### 3. Download File

**Request:**
```bash
curl -O http://localhost:8001/files/file_550e8400e29b/download
```

**Save with custom name:**
```bash
curl http://localhost:8001/files/file_550e8400e29b/download -o my_document.pdf
```

### 4. Delete File

**Request:**
```bash
curl -X DELETE http://localhost:8001/files/file_550e8400e29b
```

**Response:**
```json
{"message": "File deleted successfully", "id": "file_550e8400e29b"}
```

## Query Parameters Reference

| Parameter | Type | Example | Notes |
| --- | --- | --- | --- |
| skip | int | 0 | Pagination offset |
| limit | int | 10 | Items per page (max 100) |
| search | string | "report" | Searches filename only |
| mime_type | string | "application/pdf" | Exact MIME type match |
| tags | string | "finance,quarterly" | Filter by comma-separated tags |

## Common Issues and Troubleshooting

### Issue: 413 Payload Too Large
**Symptom:** `{"detail": "Request body too large"}`

**Cause:** File exceeds maximum upload size.

**Solution:** Use smaller files or compress before uploading.

```bash
ls -lh /path/to/file.zip
zip -r compressed.zip large_folder/
```

### Issue: 404 File Not Found
**Symptom:** `{"detail": "File not found"}`

**Solution:** List files to confirm ID exists.

```bash
curl http://localhost:8001/files | jq '.files[] | {id, filename}'
```

### Issue: Tags not preserved after upload
**Symptom:** File uploaded with tags, but list shows empty tags array.

**Solution:** Ensure tags are comma-separated without extra spaces.

```bash
curl -X POST http://localhost:8001/files/upload \
  -F "file=@doc.pdf" \
  -F "tags=finance,quarterly,2026"
```

## Endpoint Reference

| Method | Endpoint | Purpose |
| --- | --- | --- |
| POST | /files/upload | Upload one or more files |
| GET | /files | List files with optional filters |
| GET | /files/{file_id} | Get file metadata |
| GET | /files/{file_id}/download | Download file binary |
| DELETE | /files/{file_id} | Delete file and metadata |

## Related Services

- Could integrate with store_server for product images
- Could integrate with messaging_server for file sharing
