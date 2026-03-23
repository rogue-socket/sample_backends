# Sample Backends Workspace

Collection of runnable sample servers for local development, integration testing, and demo projects.

## Servers

| Folder | Purpose | Tech | Default Port |
| --- | --- | --- | --- |
| store_server | Store and checkout flow | FastAPI | 8000 |
| payments_server | Payments gateway and store callback | Flask | 5000 |
| file_upload_server | File upload and download API | FastAPI | 8001 |
| search_server | Document indexing and search API | FastAPI | 8002 |
| messaging_server | Room messaging with REST and WebSocket | FastAPI | 8003 |
| otp_auth_server | OTP auth and session token flow | FastAPI | 8004 |

## Quick Start

Run each server in its own terminal.

### Store Server (8000)

```bash
cd store_server
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```

### Payments Server (5000)

```bash
cd payments_server
pip install -r requirements.txt
python main.py
```

### File Upload Server (8001)

```bash
cd file_upload_server
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8001
```

### Search Server (8002)

```bash
cd search_server
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8002
```

### Messaging Server (8003)

```bash
cd messaging_server
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8003
```

### OTP Auth Server (8004)

```bash
cd otp_auth_server
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8004
```

## Server Skills and Agent Integration

Each server includes a `SKILL.md` file that documents:
- Core workflows and use cases
- Endpoint details and error patterns
- Integration points with other services
- Common scenarios and edge cases

**For agents and developers:** You can reference or feed a server's SKILL.md file to your agent to give it domain knowledge about that API. This enables faster and more accurate integration without manual API exploration.

Example for your agent:
```
Here is the skill file for the store server:
<contents of store_server/SKILL.md>
```

## Common Conventions

- Each project uses main.py as the entrypoint.
- Each project includes a local requirements.txt.
- Each project includes a SKILL.md file for agent/developer reference.
- FastAPI services expose interactive docs at /docs.
- Data is in-memory by default and resets on restart.

## Store to Payments Integration

1. Create a cart in the store server.
2. Add items and checkout to get order_id and total.
3. Call payments server endpoint POST /payments/orders.
4. Payments server confirms to store via POST /payments/confirm.
5. Store updates order status to paid or payment_failed.

Legacy payments route POST /pay/order is still available for compatibility.
