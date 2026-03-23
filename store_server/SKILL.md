---
name: Store Server
description: E-commerce store API for product browsing, cart management, and checkout flow with payment integration.
port: 8000
tech: FastAPI
---

# Store Server Skill

FastAPI-based e-commerce store running on port 8000. Manages products, categories, shopping carts, orders, and integrates with payments_server for payment callbacks.

## Overview

**Purpose:** Simulate a real e-commerce backend with product catalog, cart state management, and order checkout flow. Expects payments_server to handle payment processing and confirm results.

**When to Use:**
- Building and testing ecommerce frontend features (product browsing, cart, checkout)
- Testing payment integration workflows
- Creating end-to-end demo flows from product discovery to order completion
- Testing filter, search, and sort functionality

**Base URL:** http://localhost:8000

## Setup Verification

```bash
# Check service is running
curl -s http://localhost:8000/categories | jq '.[] | .name'

# Expected output (sample):
# "Electronics"
# "Clothing"
# "Home & Kitchen"
# "Books"
# "Sports & Outdoors"
```

## Core Workflows with Examples

### 1. Browse and Search Products

**Search by keyword:**
```bash
curl "http://localhost:8000/products?search=keyboard"
```

**Response:**
```json
{
  "total": 1,
  "page": 1,
  "page_size": 10,
  "products": [
    {
      "id": 3,
      "name": "Mechanical Keyboard",
      "price": 89.99,
      "rating": 4.7,
      "stock": 75
    }
  ]
}
```

**Filter by price range and rating:**
```bash
curl "http://localhost:8000/products?min_price=20&max_price=100&min_rating=4.0&sort_by=price&order=asc"
```

**Expected:** Returns products in Electronics matching criteria, sorted ascending by price.

### 2. Create Cart and Add Items

**Create new cart:**
```bash
curl -X POST http://localhost:8000/cart
```

**Response:**
```json
{
  "cart_id": "a1b2c3d4e5f6"
}
```

**Add product to cart:**
```bash
curl -X POST http://localhost:8000/cart/a1b2c3d4e5f6/items \
  -H "Content-Type: application/json" \
  -d '{"product_id": 3, "quantity": 2}'
```

**Response:**
```json
{
  "cart_id": "a1b2c3d4e5f6",
  "product_id": 3,
  "quantity": 2
}
```

**View cart contents:**
```bash
curl http://localhost:8000/cart/a1b2c3d4e5f6
```

**Response:**
```json
{
  "cart_id": "a1b2c3d4e5f6",
  "items": [
    {
      "product_id": 3,
      "name": "Mechanical Keyboard",
      "price": 89.99,
      "quantity": 2,
      "line_total": 179.98
    }
  ],
  "total": 179.98
}
```

### 3. Checkout and Create Order

**Checkout cart:**
```bash
curl -X POST http://localhost:8000/cart/a1b2c3d4e5f6/checkout
```

**Response:**
```json
{
  "order_id": "abc123def456",
  "total": 179.98,
  "message": "Send order_id and total to the payments backend to complete purchase."
}
```

**Important:** Save the order_id and total. These must be sent to payments_server.

### 4. Payment Confirmation Flow

**After payments_server processes payment, it calls:**
```bash
curl -X POST http://localhost:8000/payments/confirm \
  -H "Content-Type: application/json" \
  -d '{"order_id": "abc123def456", "status": "success"}'
```

**Response on success:**
```json
{
  "order_id": "abc123def456",
  "status": "paid",
  "message": "Payment confirmed. Stock updated."
}
```

**Verify order status:**
```bash
curl http://localhost:8000/orders/abc123def456
```

**Response:**
```json
{
  "order_id": "abc123def456",
  "cart_id": "a1b2c3d4e5f6",
  "items": [...],
  "total": 179.98,
  "status": "paid"
}
```

## Query Parameters Reference

**GET /products** supports filtering:

| Parameter | Type | Example | Notes |
| --- | --- | --- | --- |
| category_id | int | 1 | Returns only Electronics |
| brand | string | "SoundMax" | Case-insensitive |
| min_price | float | 50 | Inclusive |
| max_price | float | 150 | Inclusive |
| min_rating | float | 4.5 | 0-5 scale |
| in_stock | bool | true | Only items with stock > 0 |
| search | string | "wireless" | Searches name and description |
| sort_by | string | "price" | Options: price, rating, name |
| order | string | "asc" | Options: asc, desc |
| page | int | 2 | Pagination (starts at 1) |
| page_size | int | 20 | Max 100 per page |

## Common Issues and Troubleshooting

### Issue: Cart returns 404
**Symptom:** `{"detail": "Cart not found"}`

**Cause:** Cart ID doesn't exist or expired.

**Solution:** Create a new cart with POST /cart and save the new cart_id.

```bash
# Create and use immediately
cart_id=$(curl -s -X POST http://localhost:8000/cart | jq -r '.cart_id')
curl "http://localhost:8000/cart/$cart_id"
```

### Issue: Insufficient stock on checkout
**Symptom:** `{"detail": "Not enough stock for 'Product Name'..."}`

**Cause:** Requested quantity exceeds available inventory.

**Solution:** Reduce quantity or choose different product.

```bash
# Check product stock before adding
curl "http://localhost:8000/products/5" | jq '.stock'
```

### Issue: Checkout fails with empty cart error
**Symptom:** `{"detail": "Cart is empty"}`

**Cause:** Added items were removed or cart was never populated.

**Solution:** Add items to cart before checkout.

```bash
# Verify items before checkout
curl "http://localhost:8000/cart/YOUR_CART_ID" | jq '.items | length'
```

### Issue: Payment confirmation returns 400
**Symptom:** `{"detail": "Order already processed..."}`

**Cause:** Trying to confirm same order twice.

**Solution:** Each order can only be confirmed once. For testing, create a new order.

```bash
# Create new order for retry
curl -X POST http://localhost:8000/cart/CART_ID/checkout | jq '.order_id'
```

## Integration Pattern: Store + Payments

**Sequence:**
1. Client creates cart in store_server
2. Client adds items to cart
3. Client calls checkout → gets order_id and total
4. Client sends order_id + total to payments_server
5. payments_server processes payment
6. payments_server calls store_server /payments/confirm with result
7. store_server updates order status and inventory

**Example flow script:**
```bash
#!/bin/bash
# 1. Create cart
cart=$(curl -s -X POST http://localhost:8000/cart)
cart_id=$(echo $cart | jq -r '.cart_id')
echo "Cart ID: $cart_id"

# 2. Add item
curl -s -X POST http://localhost:8000/cart/$cart_id/items \
  -H "Content-Type: application/json" \
  -d '{"product_id": 3, "quantity": 1}'

# 3. Checkout
order=$(curl -s -X POST http://localhost:8000/cart/$cart_id/checkout)
order_id=$(echo $order | jq -r '.order_id')
total=$(echo $order | jq -r '.total')
echo "Order ID: $order_id, Total: $total"

# 4. Send to payments_server (assumes it's running on 5000)
curl -X POST http://localhost:5000/payments/orders \
  -H "Content-Type: application/json" \
  -d "{\"order_id\": \"$order_id\", \"amount\": $total}"

# 5. Check order status
sleep 1
curl http://localhost:8000/orders/$order_id | jq '.status'
```

## Related Services

- **payments_server** (port 5000): Handles payment processing and notifies store of results via POST /payments/confirm
- **file_upload_server** (port 8001): Could be used for product images (not yet integrated)
