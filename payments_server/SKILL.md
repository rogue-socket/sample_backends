---
name: Payments Server
description: Mock payments gateway with account management, order payment processing, and store callback notifications.
port: 5000
tech: Flask
---

# Payments Server Skill

Flask-based mock payments gateway running on port 5000. Manages a single mock bank account and processes order payments with automatic callback notification to store_server.

## Overview

**Purpose:** Simulate payment processing for orders from store_server. Accepts payment requests, validates funds, deducts balance, and notifies store_server of success or failure via callback.

**When to Use:**
- Testing checkout to payment confirmation workflows
- Simulating payment success and insufficient funds scenarios
- Testing store_server callback handling
- Building complete ecommerce demo flows

**Base URL:** http://localhost:5000

**Default Account:** ACC-001, Balance: 50000.0

## Setup Verification

```bash
# Check service is running and account exists
curl -s http://localhost:5000/balance | jq '.'

# Expected output:
# {
#   "status": "success",
#   "account_id": "ACC-001",
#   "holder": "John Doe",
#   "balance": 50000.0
# }
```

## Core Workflows with Examples

### 1. Check Current Balance

**Request:**
```bash
curl http://localhost:5000/balance
```

**Response:**
```json
{
  "status": "success",
  "account_id": "ACC-001",
  "holder": "John Doe",
  "balance": 50000.0
}
```

### 2. Process Store Order Payment (Key Workflow)

**Request:** After store_server checkout returns order_id and total
```bash
curl -X POST http://localhost:5000/payments/orders \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": "abc123def456",
    "amount": 179.98
  }'
```

**Response (Success - Sufficient Funds):**
```json
{
  "status": "success",
  "message": "Payment of 179.98 for order abc123def456 completed",
  "balance": 49820.02,
  "transaction": {
    "order_id": "abc123def456",
    "amount": 179.98,
    "balance_after": 49820.02
  },
  "shop_notified": true
}
```

**Response (Failure - Insufficient Funds):**
```json
{
  "status": "failed",
  "message": "Insufficient funds",
  "balance": 49820.02,
  "requested": 51000
}
```

**Behind the scenes:** If successful, payments_server automatically calls:
```bash
POST http://localhost:8000/payments/confirm
{"order_id": "abc123def456", "status": "success"}
```

**Or on failure:**
```bash
POST http://localhost:8000/payments/confirm
{"order_id": "abc123def456", "status": "failed"}
```

### 3. Generic Payment (Non-Order)

**Request:**
```bash
curl -X POST http://localhost:5000/pay \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 100,
    "recipient": "https://example-shop.com"
  }'
```

**Response:**
```json
{
  "status": "success",
  "message": "Payment of 100 to https://example-shop.com completed",
  "balance": 49720.02,
  "transaction": {
    "recipient": "https://example-shop.com",
    "amount": 100,
    "balance_after": 49720.02
  }
}
```

### 4. View Transaction History

**Request:**
```bash
curl http://localhost:5000/transactions
```

**Response:**
```json
{
  "status": "success",
  "account_id": "ACC-001",
  "transactions": [
    {
      "order_id": "abc123def456",
      "amount": 179.98,
      "balance_after": 49820.02
    },
    {
      "recipient": "https://example-shop.com",
      "amount": 100,
      "balance_after": 49720.02
    }
  ]
}
```

### 5. Reset Account (Testing Only)

**Request:**
```bash
curl -X POST http://localhost:5000/reset
```

**Response:**
```json
{
  "status": "success",
  "message": "Account reset to default balance",
  "balance": 50000.0
}
```

## Common Issues and Troubleshooting

### Issue: 402 Payment fails with "Insufficient funds"
**Symptom:** 
```json
{"status": "failed", "message": "Insufficient funds", "balance": 100, "requested": 5000}
```

**Cause:** Account balance is less than requested payment amount.

**Solution:** Reset account or use smaller payment amount.

```bash
# Check current balance
curl http://localhost:5000/balance | jq '.balance'

# Reset to start fresh
curl -X POST http://localhost:5000/reset
```

### Issue: 400 Missing fields error
**Symptom:** 
```json
{"status": "failed", "message": "Both 'order_id' and 'amount' fields are required"}
```

**Cause:** POST request missing required fields.

**Solution:** Verify request JSON has both order_id and amount.

```bash
# Correct format
curl -X POST http://localhost:5000/payments/orders \
  -H "Content-Type: application/json" \
  -d '{"order_id": "ord_123", "amount": 99.99}'
```

### Issue: callback to store_server fails
**Symptom:** Payment succeeds locally but `shop_notified` is false.

**Cause:** store_server is not running or not on expected port.

**Solution:** Verify store_server is running on port 8000.

```bash
# Check store_server health
curl http://localhost:8000/categories

# If fails, start store_server:
# cd store_server && python -m uvicorn main:app --reload --port 8000
```

### Issue: Cannot deduct amount or transaction seems stuck
**Symptom:** Payment request hangs or returns unexpected error.

**Cause:** Service connectivity issue or bad JSON.

**Solution:** Verify JSON is valid and service is responsive.

```bash
# Test connectivity
curl -v http://localhost:5000/balance

# Validate JSON syntax
echo '{"order_id": "ord_123", "amount": 99.99}' | jq .
```

## Integration Pattern: Complete Checkout + Payment Flow

**Sequence:**
1. Client gets order_id and total from store_server checkout
2. Client calls payments_server POST /payments/orders with order_id and amount
3. payments_server deducts balance
4. payments_server calls store_server /payments/confirm with status
5. store_server updates order and inventory
6. Client can verify order status in store_server

**Complete example script:**
```bash
#!/bin/bash

# Assume store_server has created cart and checkout
order_id="abc123def456"
total=179.98

echo "Processing payment for order: $order_id, amount: $total"

# Pay via payments_server
payment=$(curl -s -X POST http://localhost:5000/payments/orders \
  -H "Content-Type: application/json" \
  -d "{\"order_id\": \"$order_id\", \"amount\": $total}")

echo "Payment response:"
echo $payment | jq '.'

# Check if notified store
shop_notified=$(echo $payment | jq '.shop_notified')
if [ "$shop_notified" = "true" ]; then
  echo "✓ Store was notified, checking order status..."
  sleep 1
  curl -s http://localhost:8000/orders/$order_id | jq '.status'
else
  echo "✗ Store notification failed"
fi
```

## Endpoint Reference

| Method | Endpoint | Purpose | Required Fields |
| --- | --- | --- | --- |
| GET | /balance | Check account balance | None |
| POST | /pay | Generic payment | amount, recipient |
| POST | /payments/orders | Pay for store order | order_id, amount |
| POST | /pay/order | Legacy order payment | order_id, amount |
| GET | /transactions | View all transactions | None |
| POST | /reset | Reset account to default | None |

## Related Services

- **store_server** (port 8000): Sends checkout orders here for payment, receives callbacks at /payments/confirm
