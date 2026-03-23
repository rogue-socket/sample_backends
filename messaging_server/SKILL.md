---
name: Messaging Server
description: Room-based chat with REST and WebSocket support.
port: 8003
tech: FastAPI
---

# Messaging Server

Room-based messaging API running on port 8003. Supports both REST polling and WebSocket-based real-time messaging with presence events.

## When to Use

- Testing chat and messaging UI
- Building real-time collaboration features
- Testing WebSocket connections and fallbacks
- Simulating multi-user presence and typing indicators

## Core Workflows

### Create Room
POST /rooms with {name} → returns room with id and created_at.

### List Rooms
GET /rooms → returns all rooms.

### Send Message (REST)
POST /rooms/{room_id}/messages with {sender, text} → broadcasts to all connected WebSocket clients in room and stores in history.

### View Message History
GET /rooms/{room_id}/messages with optional limit query param → returns recent messages (default last 50).

### Join Room (WebSocket)
WS /ws/rooms/{room_id}?username=<name> → accepts connection and broadcasts join event. While connected, relays incoming text as messages to all clients in room and broadcasts leave event on disconnect.

## Health Check

GET /health returns service health status.

## WebSocket Messages

Messages received on WebSocket:
- Any text → becomes a chat message with sender=username and sent_at
- Broadcasts to all clients in room: {type: "message", payload: {id, room_id, sender, text, sent_at}}
- On join: {type: "presence", payload: {event: "joined", room_id, username, at}}
- On leave: {type: "presence", payload: {event: "left", room_id, username, at}}

## Common Errors

- 404 on POST /rooms/{id}/messages if room doesn't exist
- 404 on GET /rooms/{id}/messages if room doesn't exist
- WebSocket code 1008 if room doesn't exist when connecting
