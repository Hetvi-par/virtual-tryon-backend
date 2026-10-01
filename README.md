# Virtual Try-On — Backend

FastAPI + Postgres service that serves the product catalog and model photos for the
[frontend](https://github.com/Hetvi-par/virtual-tryon-frontend).

```
server.py        API routes
database.py      DB connection + tables
seed.py          loads products, shades and model photos
Dockerfile       API image
docker-compose.yml  Postgres (and optionally the API)
```

The seed reads `../frontend/public/catalog.json`, so clone both repos side by side:

```
virtual-tryon/
├── frontend/   (virtual-tryon-frontend)
└── backend/    (virtual-tryon-backend)
```

Set `CATALOG_PATH` to point somewhere else.

## Run locally

```
docker compose up -d db
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python seed.py --reset
python -m uvicorn server:app --port 8001
```

API on http://localhost:8001, docs at `/docs`.

## API

| Method | Path | |
|---|---|---|
| GET | `/api/products` | products with shades |
| POST | `/api/products/{key}/shades` | add a shade |
| DELETE | `/api/shades/{id}` | remove a shade |
| GET | `/api/model-photos` | model photo gallery |
