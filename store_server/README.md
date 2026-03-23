# Sample Store Server

FastAPI server with sample categories, products, cart operations, checkout, and payment confirmation.

## Run

```bash
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```

Docs: http://localhost:8000/docs

## Health

- GET /categories can be used as a basic readiness check.

## Key Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | /categories | List categories |
| GET | /categories/{category_id} | Get one category |
| GET | /products | List products with filter/search/sort |
| GET | /products/{product_id} | Get one product |
| GET | /products/{product_id}/related | Related products |
| GET | /brands | List brands |
| POST | /cart | Create cart |
| GET | /cart/{cart_id} | View cart |
| POST | /cart/{cart_id}/items | Add item to cart |
| DELETE | /cart/{cart_id}/items/{product_id} | Remove cart item |
| POST | /cart/{cart_id}/checkout | Checkout cart |
| GET | /orders/{order_id} | Get order status |
| POST | /payments/confirm | Payment callback from payments server |

## Product Query Parameters

GET /products supports these optional parameters:

- category_id
- brand
- min_price
- max_price
- min_rating
- in_stock
- search
- sort_by (price, rating, name)
- order (asc, desc)
- page
- page_size

## Quick Examples

```bash
curl "http://localhost:8000/products?search=keyboard"

curl -X POST http://localhost:8000/cart

curl -X POST http://localhost:8000/payments/confirm \
  -H "Content-Type: application/json" \
  -d '{"order_id":"ord_123","status":"success"}'
```

## Integration Notes

- This server is designed to work with payments_server.
- Payments server calls POST /payments/confirm after processing payment.
- Data is stored in memory and resets on restart.
