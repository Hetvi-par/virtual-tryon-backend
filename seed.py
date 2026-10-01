"""Fill an empty database with the starter catalog. Safe to run more than once."""

from sqlalchemy import select

from database import ModelPhoto, Product, SessionLocal, Shade, init_db

PRODUCTS = [
    ("lips", "lipstick", "#b3122f", 0.8, "matte", [
        ("Rose nude", "#c4787f"), ("Classic red", "#b3122f"), ("Berry", "#7d1f4b"), ("Coral", "#e0644f"),
        ("Plum", "#5e1a3c"), ("Mauve", "#a05a7a"), ("Brick", "#9a3b2c"), ("Hot pink", "#d81b78"),
    ]),
    ("blush", "blush", "#e88a99", 0.5, None, [
        ("Peach", "#f2a58e"), ("Rose", "#e88a99"), ("Coral", "#ee7a6a"), ("Berry", "#b8506e"),
        ("Soft pink", "#f4b6c2"), ("Terracotta", "#c8705a"), ("Mauve", "#b56b8a"), ("Plum", "#8e3f62"),
    ]),
    ("eye", "eyeshadow", "#6d3a66", 0.6, None, [
        ("Taupe", "#8a6a5c"), ("Plum", "#6d3a66"), ("Bronze", "#a0693a"), ("Navy", "#2d3f73"),
        ("Rose gold", "#c98a7c"), ("Olive", "#6b6b3a"), ("Smoky", "#3a3440"), ("Lilac", "#9a7cc0"),
    ]),
]

MODEL_PHOTOS = [(f"Model {i}", f"/models/model{i}.jpg") for i in range(1, 7)]


def seed():
    init_db()
    with SessionLocal() as db:
        if db.scalar(select(Product).limit(1)) is None:
            for sort, (key, label, color, opacity, finish, shades) in enumerate(PRODUCTS):
                db.add(Product(
                    key=key, label=label, color=color, opacity=opacity, finish=finish, sort=sort,
                    shades=[Shade(name=n, hex=h, sort=i) for i, (n, h) in enumerate(shades)],
                ))
            print("Seeded products and shades")
        if db.scalar(select(ModelPhoto).limit(1)) is None:
            db.add_all(ModelPhoto(name=n, src=s, sort=i) for i, (n, s) in enumerate(MODEL_PHOTOS))
            print("Seeded model photos")
        db.commit()


if __name__ == "__main__":
    seed()
