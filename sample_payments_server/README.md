# Sample Payments Server

Flask server that simulates a payments account and can notify the store server after order payments.

## Run

```bash
pip install -r requirements.txt
python main.py
```

Base URL: http://localhost:5000

## Health

- GET /balance can be used as a basic readiness check.

## Key Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | /balance | Current account balance |
| POST | /pay | Generic payment to a recipient |
| POST | /payments/orders | Pay store order and notify store callback |
| POST | /pay/order | Legacy alias for /payments/orders |
| GET | /transactions | List payment history |
| POST | /reset | Reset account and transactions |

## Request Payloads

POST /pay body:

- amount (number, required)
- recipient (string, required)

POST /payments/orders body:

- order_id (string, required)
- amount (number, required)

## Quick Examples

```bash
curl http://localhost:5000/balance

curl -X POST http://localhost:5000/pay \
  -H "Content-Type: application/json" \
  -d '{"amount":1500,"recipient":"https://example-shop.com"}'

curl -X POST http://localhost:5000/payments/orders \
  -H "Content-Type: application/json" \
  -d '{"order_id":"ord_abc123","amount":2500}'
```

## Integration Notes

- On order payment, this server calls store callback endpoint POST http://localhost:8000/payments/confirm.
- On insufficient funds for order payments, callback is sent with failed status.
- Data is stored in memory and resets on restart.
