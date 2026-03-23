---
name: Messaging Server
description: Room-based chat service with REST and WebSocket real-time messaging.
port: 8003
tech: FastAPI
---

# Messaging Server Skill

FastAPI-based real-time messaging service running on port 8003. Provides room-based chat with REST API for operations and WebSocket for live message streaming.

## Overview

**Purpose:** Enable real-time chat in rooms with REST management and WebSocket event streaming. Tracks room members and broadcasts messages to all connected clients.

**When to Use:**
- Building chat or collaboration features
- Testing real-time messaging and WebSocket handling
- Implementing room-based group chat
- Testing presence and join/leave notifications

**Base URL:** http://localhost:8003

**WebSocket URL:** ws://localhost:8003/ws/rooms/{room_id}?username=USERNAME

**Storage:** Rooms and messages stored in-memory (lost on restart)

## Setup Verification

```bash
# Check service is running
curl -s http://localhost:8003/rooms | jq '.'

# Expected: empty array initially
```

## Core Workflows with Examples

### 1. Create Room

**Request:**
```bash
curl -X POST http://localhost:8003/rooms \
  -H "Content-Type: application/json" \
  -d '{
    "name": "General Discussion",
    "description": "Main chat room for all users"
  }'
```

**Response:**
```json
{
  "id": "room_a1b2c3d4",
  "name": "General Discussion",
  "description": "Main chat room for all users",
  "created_at": "2026-03-24T10:30:45Z",
  "members_count": 0
}
```

### 2. List Rooms

**Request:**
```bash
curl http://localhost:8003/rooms
```

**Response:**
```json
[
  {
    "id": "room_a1b2c3d4",
    "name": "General Discussion",
    "description": "Main chat room",
    "created_at": "2026-03-24T10:30:45Z",
    "members_count": 2
  }
]
```

### 3. Get Room Details and Message History

**Request:**
```bash
curl "http://localhost:8003/rooms/room_a1b2c3d4/messages"
```

**Response:**
```json
{
  "room_id": "room_a1b2c3d4",
  "room_name": "General Discussion",
  "members_count": 2,
  "messages": [
    {
      "id": "msg_001",
      "username": "alice",
      "message": "Hello everyone!",
      "timestamp": "2026-03-24T10:31:00Z"
    },
    {
      "id": "msg_002",
      "username": "bob",
      "message": "Hi Alice! Welcome to the room.",
      "timestamp": "2026-03-24T10:31:15Z"
    }
  ]
}
```

### 4. Connect via WebSocket (Real-Time Messaging) - Core Workflow

**Connect to room:**
```bash
ws://localhost:8003/ws/rooms/room_a1b2c3d4?username=alice
```

**Using websocat (command-line WebSocket client):**
```bash
# Terminal 1: Alice joins
websocat "ws://localhost:8003/ws/rooms/room_a1b2c3d4?username=alice"

# Terminal 2: Bob joins same room
websocat "ws://localhost:8003/ws/rooms/room_a1b2c3d4?username=bob"

# Terminal 1 or 2: Send message (type and hit enter)
Hello from Alice!
```

**Using Python websockets:**
```python
import asyncio
import websockets
import json

async def main():
    async with websockets.connect('ws://localhost:8003/ws/rooms/room_a1b2c3d4?username=alice') as ws:
        # Receive events
        async for event in ws:
            print(json.loads(event))
        
        # Send message
        await ws.send("Hello!")

asyncio.run(main())
```

### WebSocket Event Types

**User Joined:**
```json
{
  "type": "user_joined",
  "username": "alice",
  "message": "alice joined the room"
}
```

**User Left:**
```json
{
  "type": "user_left",
  "username": "alice",
  "message": "alice left the room"
}
```

**Message Event:**
```json
{
  "type": "message",
  "username": "alice",
  "message": "Hello everyone!",
  "timestamp": "2026-03-24T10:31:00Z"
}
```

## Common Issues and Troubleshooting

### Issue: WebSocket connection refused
**Symptom:** `Error: Failed to connect to ws://localhost:8003/ws/...`

**Cause:** Server not running or wrong port/URL format.

**Solution:** Verify server is running and use correct WebSocket protocol (ws:// not http://).

```bash
# Check server
curl http://localhost:8003/rooms

# Correct WebSocket URL format
ws://localhost:8003/ws/rooms/{room_id}?username={name}
# NOT: http://localhost:8003/ws/...
```

### Issue: Message appears for author but not other users
**Symptom:** User A sends message, sees it in their client, but User B doesn't receive it.

**Cause:** User B's WebSocket client disconnected or hasn't connected yet.

**Solution:** Verify both users are connected via WebSocket. REST endpoints don't broadcast.

```bash
# Check room has members
curl http://localhost:8003/rooms/room_a1b2c3d4

# REST /messages endpoint shows history, not real-time
# Use WebSocket for live messaging
```

### Issue: Missing message history
**Symptom:** Connect to room and see no previous messages.

**Cause:** WebSocket only shows new messages after connection. Use REST to get history.

**Solution:** Fetch message history via REST before/after WebSocket connection.

```bash
# Get history via REST
curl http://localhost:8003/rooms/room_a1b2c3d4/messages

# Then connect WebSocket for new messages
ws://localhost:8003/ws/rooms/room_a1b2c3d4?username=alice
```

### Issue: WebSocket closes unexpectedly
**Symptom:** Connection drops after a few messages.

**Cause:** Network issue, client timeout, or server restart.

**Solution:** Implement reconnection logic in client.

### Issue: Room not found when connecting
**Symptom:** `{"detail": "Room not found"}`

**Cause:** WebSocket URL has wrong room_id.

**Solution:** List rooms to get correct ID.

```bash
# Get correct room IDs
curl http://localhost:8003/rooms | jq '.[] | {id, name}'

# Use correct ID in WebSocket URL
ws://localhost:8003/ws/rooms/CORRECT_ROOM_ID?username=alice
```

## Endpoint Reference

| Method | Endpoint | Purpose |
| --- | --- | --- |
| POST | /rooms | Create new room |
| GET | /rooms | List all rooms |
| GET | /rooms/{room_id}/messages | Get message history for room |
| WS | /ws/rooms/{room_id}?username=USERNAME | Connect for real-time messaging |

## WebSocket Message Format

After connecting, simply send plain text messages. Server broadcasts them as:
```json
{"type": "message", "username": "...", "message": "...", "timestamp": "..."}
```

## Related Services

- Could integrate file_upload_server for sharing files in chat
- Could integrate otp_auth_server for user authentication before chat access
- 404 on GET /rooms/{id}/messages if room doesn't exist
- WebSocket code 1008 if room doesn't exist when connecting
