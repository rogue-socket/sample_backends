---
name: Search Server
description: Document indexing and full-text search service with keyword ranking.
port: 8002
tech: FastAPI
---

# Search Server Skill

FastAPI-based search and document indexing service running on port 8002. Provides simple full-text search with keyword matching, filtering, and result ranking.

## Overview

**Purpose:** Index documents and perform ranked keyword searches. Stores documents in memory with search index. Useful for testing search-driven UIs and autocomplete features.

**When to Use:**
- Testing product search interfaces
- Building document discovery features
- Implementing search filtering workflows
- Testing keyword ranking and relevance

**Base URL:** http://localhost:8002

**Storage:** Documents stored in-memory (lost on restart)

## Setup Verification

```bash
# Check service is running
curl -s http://localhost:8002/documents | jq '.total'

# Expected: 0 initially
```

## Core Workflows with Examples

### 1. Create Documents

**Single document:**
```bash
curl -X POST http://localhost:8002/documents \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Getting Started with FastAPI",
    "content": "FastAPI is a modern web framework for building APIs with Python using standard Python type hints.",
    "tags": ["python", "fastapi", "tutorial"],
    "category": "programming"
  }'
```

**Response:**
```json
{
  "id": "doc_1a2b3c4d",
  "title": "Getting Started with FastAPI",
  "content": "FastAPI is a modern web framework...",
  "tags": ["python", "fastapi", "tutorial"],
  "category": "programming",
  "created_at": "2026-03-24T10:30:45Z"
}
```

### 2. List Documents

**Get all documents:**
```bash
curl "http://localhost:8002/documents"
```

**With pagination:**
```bash
curl "http://localhost:8002/documents?skip=0&limit=5"
```

### 3. Search Documents (Core Workflow)

**Simple keyword search:**
```bash
curl "http://localhost:8002/search?q=fastapi"
```

**Response (Ranked Results):**
```json
{
  "query": "fastapi",
  "total_results": 2,
  "results": [
    {
      "id": "doc_1a2b3c4d",
      "title": "Getting Started with FastAPI",
      "content": "FastAPI is a modern web framework...",
      "tags": ["python", "fastapi", "tutorial"],
      "relevance_score": 0.95,
      "match_locations": ["title", "content", "tags"]
    }
  ]
}
```

**Multi-word search:**
```bash
curl "http://localhost:8002/search?q=python+web+framework"
```

**Search with category filter:**
```bash
curl "http://localhost:8002/search?q=database&category=databases"
```

### 4. Get Document Details

**Request:**
```bash
curl "http://localhost:8002/documents/doc_1a2b3c4d"
```

## Query Parameters Reference

**Search Endpoint (GET /search)**

| Parameter | Type | Example | Notes |
| --- | --- | --- | --- |
| q | string | "fastapi tutorial" | Search keywords (required) |
| category | string | "programming" | Filter by category |
| skip | int | 0 | Pagination offset |
| limit | int | 10 | Results per page (max 50) |

**List Endpoint (GET /documents)**

| Parameter | Type | Example | Notes |
| --- | --- | --- | --- |
| skip | int | 0 | Pagination offset |
| limit | int | 10 | Items per page (max 50) |

## Common Issues and Troubleshooting

### Issue: Search returns empty results
**Symptom:** `{"query": "...", "total_results": 0, "results": []}`

**Solution:** Create documents first, then search with matching keywords.

```bash
# Create test document
curl -X POST http://localhost:8002/documents \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Python Tutorial",
    "content": "Learn Python programming fundamentals",
    "tags": ["python"],
    "category": "programming"
  }'

# Now search
curl "http://localhost:8002/search?q=python"
```

### Issue: Special characters break search
**Symptom:** Searching "C++" or "Node.js" returns no results.

**Solution:** Try searching partial word or use category filter instead.

```bash
curl "http://localhost:8002/search?q=programming"
curl "http://localhost:8002/search?q=language&category=programming"
```

### Issue: Pagination shows wrong total_results
**Symptom:** total_results shows 50, but only 5 items returned with limit=5.

**Solution:** Use skip/limit to iterate through pages correctly.

```bash
curl "http://localhost:8002/documents?skip=0&limit=5"    # page 1
curl "http://localhost:8002/documents?skip=5&limit=5"    # page 2
curl "http://localhost:8002/documents?skip=10&limit=5"   # page 3
```

## Endpoint Reference

| Method | Endpoint | Purpose |
| --- | --- | --- |
| POST | /documents | Create new document |
| GET | /documents | List all documents |
| GET | /documents/{doc_id} | Get document details |
| GET | /search | Search documents by keyword |

## Related Services

- Could integrate with file_upload_server to index uploaded documents
- Could power search features in store_server product catalog

## Ranking Logic

Simple keyword-based ranking. Not intended for production relevance algorithms.
