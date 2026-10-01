"""Fill an empty database with the starter catalog. Safe to run more than once.

Usage (from the backend folder):
    python scripts/seed.py            seed empty tables
    python scripts/seed.py --reset    drop and recreate all tables first

The catalog comes from data/catalog.json (override with CATALOG_PATH). Keep it in step with the
frontend's public/catalog.json, which the frontend falls back to when the API is down.
"""

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))   # so `database` imports when run as scripts/seed.py

from sqlalchemy import select  # noqa: E402

from database import Base, ModelPhoto, Product, SessionLocal, Shade, engine, init_db  # noqa: E402

CATALOG = Path(os.getenv("CATALOG_PATH", ROOT / "data" / "catalog.json"))
MODEL_PHOTOS = [(f"Model {i}", f"/models/model{i}.jpg") for i in range(1, 7)]


def seed(reset: bool = False):
    if reset:
        Base.metadata.drop_all(engine)
        print("Dropped all tables")
    init_db()
    with SessionLocal() as db:
        if db.scalar(select(Product).limit(1)) is None:
            for sort, p in enumerate(json.loads(CATALOG.read_text(encoding="utf-8"))):
                db.add(Product(
                    slug=p["id"], type=p["type"], name=p["name"], finish=p["finish"], price=p["price"],
                    defaults=p.get("defaults"), sort=sort,
                    shades=[
                        Shade(name=s["name"], code=s["code"], hex=s["hex"].lower(), metallic=s.get("metallic", False),
                              lash=s.get("lash"), sort=i)
                        for i, s in enumerate(p["shades"])
                    ],
                ))
            print("Seeded products and shades")
        if db.scalar(select(ModelPhoto).limit(1)) is None:
            db.add_all(ModelPhoto(name=n, src=s, sort=i) for i, (n, s) in enumerate(MODEL_PHOTOS))
            print("Seeded model photos")
        db.commit()


if __name__ == "__main__":
    seed(reset="--reset" in sys.argv)
