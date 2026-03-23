---
name: Payments Server
description: Mock payments gateway with account balance and order payment callbacks.
port: 5000
tech: Flask
---

# Payments Server

Payments gateway API running on port 5000. Manages a mock bank account and processes payments for orders, notifying the store_server of results.

## When to Use

- Testing payment flow in ecommerce checkouts
- Simulating payment success/failure scenarios
- Testing callbacks and async notifications
- Building payment integration test scenarios

## Core Workflows

### Check Account Balance
GET /balance → returns current account balance (default 50000.0).

### Make Generic Payment
POST /pay with {amount, recipient} → deducts from balance and records transaction.

### Pay Store Order (with callback)
POST /payments/orders with {order_id, amount} → deducts balance and immediately calls store_server at POST http://localhost:8000/payments/confirm with {order_id, status: "success"} or "failed".

Alternatively, POST /pay/order is available for backward compatibility.

### View Transactions
GET /transactions → lists all payment history.

### Reset Account
POST /reset → resets balance to 50000.0 and clears transaction history.

## Health Check

GET /balance is always available and can be used as a readiness probe.

## Common Errors

- 402 on POST /pay or POST /payments/orders if insufficient funds (balance < amount)
- 400 if request body is missing required fields

## Integration Points

- Calls POST http://localhost:8000/payments/confirm to notify store_server after order payment
- Works in tandem with store_server checkout flow
