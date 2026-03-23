# Sample Messaging Server

FastAPI server for room-based chat using REST plus WebSocket realtime channels.

## Run

```bash
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8003
```

Docs: http://localhost:8003/docs

## Health

- GET /health

## Key Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | /health | Service health check |
| POST | /rooms | Create room |
| GET | /rooms | List rooms |
| POST | /rooms/{room_id}/messages | Send room message over REST |
| GET | /rooms/{room_id}/messages | List message history |
| WS | /ws/rooms/{room_id}?username=alice | Realtime room channel |

## Quick Example

```bash
curl -X POST http://localhost:8003/rooms \
  -H "Content-Type: application/json" \
  -d '{"name":"general"}'
```

## Notes

- WebSocket endpoint broadcasts join, leave, and message events.
- Messages and room data are in memory and reset on restart.
