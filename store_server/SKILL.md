---
name: Store Server
description: E-commerce store with products, cart, and checkout flow.
port: 8000
tech: FastAPI
---

# Store Server

E-commerce store API running on port 8000. Tracks products, categories, carts, orders, and integrates with payments_server for payment confirmation.

## When to Use

- Testing product browsing and filtering workflows
- Implementing shopping cart and checkout features
- Integration testing with a payments gateway
- Building mockups of ecommerce frontends

## Core Workflows

### Browse Products
GET /products with optional filters: category_id, brand, min_price, max_price, min_rating, in_stock, search, sort_by, order, page, page_size.

### Create and Manage Cart
1. POST /cart → returns cart_id
2. POST /cart/{cart_id}/items with {product_id, quantity}
3. GET /cart/{cart_id} to view contents
4. DELETE /cart/{cart_id}/items/{product_id} to remove

### Checkout
POST /cart/{cart_id}/checkout → returns order_id and total. Send this order_id and total to payments_server.

### Payment Confirmation (called by payments_server)
POST /payments/confirm with {order_id, status} where status is "success" or "failed". Reduces inventory on success.

## Health Check

GET /categories is always available and can be used as a readiness probe.

## Common Errors

- 404 on /products/{product_id} if not found
- 404 on /cart/{cart_id} if cart doesn't exist
- 400 on checkout if cart is empty or insufficient stock
- 404 on /payments/confirm if order_id not in pending_payment status

## Integration Points

- Sends order_id and total to payments_server after checkout
- Receives payment confirmation callback from payments_server on POST /payments/confirm
