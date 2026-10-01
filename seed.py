"""Fill an empty database with the starter catalog. Safe to run more than once.

The catalog comes from frontend/public/catalog.json, the same file the frontend falls back to
when the API is down (override with CATALOG_PATH). Run with --reset to drop and recreate all tables first.
"""

import json
import os
import sys
from pathlib import Path

from sqlalchemy import select

from database import Base, ModelPhoto, Product, SessionLocal, Shade, engine, init_db

CATALOG = Path(os.getenv(
    "CATALOG_PATH", Path(__file__).resolve().parent.parent / "frontend" / "public" / "catalog.json"
))
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
                    slug=p["id"], type=p["type"], name=p["name"], finish=p["finish"], price=p["price"], sort=sort,
                    shades=[
                        Shade(name=s["name"], code=s["code"], hex=s["hex"].lower(), metallic=s.get("metallic", False), sort=i)
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
