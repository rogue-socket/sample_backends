---
name: Search Server
description: Simple document indexing and ranked text search.
port: 8002
tech: FastAPI
---

# Search Server

Document search and indexing API running on port 8002. Stores documents and performs simple ranked text search across title, content, and tags.

## When to Use

- Testing search functionality in UIs
- Building search result rankings and relevance
- Testing document tagging and filtering
- Simulating autocomplete or search-as-you-type features

## Core Workflows

### Create Document
POST /documents with {title, content, tags: []} → returns document with id and created_at.

### List Documents
GET /documents with optional pagination: limit (1-100, default 20), offset (default 0) → returns paginated document list.

### Get Document
GET /documents/{document_id} → returns full document.

### Delete Document
DELETE /documents/{document_id} → removes document.

### Search Documents
GET /search?q=<query> with optional tag filter → returns ranked results by relevance score. Score is calculated by:
- title matches count × 3
- content matches count × 1
- tag exact matches × 2

Results are sorted by score descending and limited to query params: limit (1-50, default 10).

## Health Check

GET /health returns service health status.

## Common Errors

- 404 on GET /documents/{id} if document not found
- 404 on DELETE if document not found
- 400 on search if query q parameter is missing or empty

## Ranking Logic

Simple keyword-based ranking. Not intended for production relevance algorithms.
