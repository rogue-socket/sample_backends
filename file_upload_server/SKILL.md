---
name: File Upload Server
description: File upload, metadata storage, download, and delete operations.
port: 8001
tech: FastAPI
---

# File Upload Server

File upload and storage API running on port 8001. Handles multipart file uploads, stores files on disk, and provides metadata lookup and download.

## When to Use

- Testing file upload functionality in forms
- Building file management UI and features
- Simulating avatar/profile picture uploads
- Testing document upload workflows

## Core Workflows

### Upload File
POST /files/upload with multipart form-data (field name: file) → returns file metadata including file_id, original_name, size_bytes, uploaded_at.

### List Uploaded Files
GET /files with optional query params: filename (substring match), content_type (exact match) → returns paginated list of file metadata.

### Get File Metadata
GET /files/{file_id} → returns full metadata for a file.

### Download File
GET /files/{file_id}/download → streams file to client with original filename and content-type.

### Delete File
DELETE /files/{file_id} → removes file from disk and metadata store.

## Health Check

GET /health returns service health status.

## Common Errors

- 400 if file has no filename or upload fails
- 404 if file_id doesn't exist
- 404 on download if file is missing on disk (orphaned metadata)

## Storage

- Uploaded files are stored in ./uploads/ relative to server directory
- Metadata (original_name, size, timestamp) is stored in memory
- Files persist on disk across server restarts; metadata does not
