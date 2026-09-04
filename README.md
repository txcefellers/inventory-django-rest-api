# Inventory Management Django API

Django REST Framework API for managing suppliers, products, stock levels, and inventory
transactions (stock in/out/adjustment), with a low-stock alert endpoint.

## Setup

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser   # optional, for /admin/
python manage.py runserver
```

Set `DJANGO_SECRET_KEY` and `DJANGO_DEBUG` environment variables for any non-local deployment
(a development-only fallback secret key is used otherwise).

## Endpoints

All endpoints are under `/api/` (browsable via Django admin at `/admin/`):

- `/api/suppliers/` — CRUD
- `/api/products/` — CRUD
- `/api/stocks/` — CRUD
- `/api/transactions/` — CRUD (adjusts stock quantity automatically)
- `/api/low-stock-alerts/` — GET, lists products at or below their reorder level
