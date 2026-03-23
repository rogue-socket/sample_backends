from datetime import UTC, datetime
import uuid

from fastapi import FastAPI, HTTPException, Query, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field

app = FastAPI(title="Sample Messaging Server")

ROOMS: dict[str, dict] = {}
MESSAGES: dict[str, list[dict]] = {}
CONNECTIONS: dict[str, set[WebSocket]] = {}


class RoomCreate(BaseModel):
    name: str = Field(min_length=1)


class MessageCreate(BaseModel):
    sender: str = Field(min_length=1)
    text: str = Field(min_length=1)


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "messaging"}


@app.post("/rooms")
def create_room(payload: RoomCreate):
    room_id = uuid.uuid4().hex[:8]
    room = {
        "id": room_id,
        "name": payload.name,
        "created_at": datetime.now(UTC).isoformat(),
    }
    ROOMS[room_id] = room
    MESSAGES[room_id] = []
    CONNECTIONS[room_id] = set()
    return room


@app.get("/rooms")
def list_rooms():
    return {
        "total": len(ROOMS),
        "rooms": list(ROOMS.values()),
    }


@app.post("/rooms/{room_id}/messages")
async def send_message(room_id: str, payload: MessageCreate):
    if room_id not in ROOMS:
        raise HTTPException(status_code=404, detail="Room not found")

    message = {
        "id": uuid.uuid4().hex,
        "room_id": room_id,
        "sender": payload.sender,
        "text": payload.text,
        "sent_at": datetime.now(UTC).isoformat(),
    }
    MESSAGES[room_id].append(message)

    disconnected_clients = []
    for socket in CONNECTIONS[room_id]:
        try:
            await socket.send_json({"type": "message", "payload": message})
        except RuntimeError:
            disconnected_clients.append(socket)

    for socket in disconnected_clients:
        CONNECTIONS[room_id].discard(socket)

    return message


@app.get("/rooms/{room_id}/messages")
def list_messages(room_id: str, limit: int = Query(50, ge=1, le=200)):
    if room_id not in ROOMS:
        raise HTTPException(status_code=404, detail="Room not found")
    return {
        "room_id": room_id,
        "messages": MESSAGES[room_id][-limit:],
    }


@app.websocket("/ws/rooms/{room_id}")
async def room_websocket(websocket: WebSocket, room_id: str, username: str = "guest"):
    if room_id not in ROOMS:
        await websocket.close(code=1008)
        return

    await websocket.accept()
    CONNECTIONS[room_id].add(websocket)

    join_event = {
        "type": "presence",
        "payload": {
            "event": "joined",
            "room_id": room_id,
            "username": username,
            "at": datetime.now(UTC).isoformat(),
        },
    }

    for socket in CONNECTIONS[room_id]:
        await socket.send_json(join_event)

    try:
        while True:
            text = await websocket.receive_text()
            message = {
                "id": uuid.uuid4().hex,
                "room_id": room_id,
                "sender": username,
                "text": text,
                "sent_at": datetime.now(UTC).isoformat(),
            }
            MESSAGES[room_id].append(message)
            for socket in CONNECTIONS[room_id]:
                await socket.send_json({"type": "message", "payload": message})
    except WebSocketDisconnect:
        CONNECTIONS[room_id].discard(websocket)
        leave_event = {
            "type": "presence",
            "payload": {
                "event": "left",
                "room_id": room_id,
                "username": username,
                "at": datetime.now(UTC).isoformat(),
            },
        }
        for socket in CONNECTIONS[room_id]:
            await socket.send_json(leave_event)
