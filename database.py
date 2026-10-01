import os

from dotenv import load_dotenv
from sqlalchemy import Boolean, ForeignKey, Integer, Numeric, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://tryon:tryon@localhost:5432/tryon")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String(64), unique=True)        # "velvet", "powderblush", ...
    type: Mapped[str] = mapped_column(String(16))                     # "lipstick" | "shadow" | "blush"
    name: Mapped[str] = mapped_column(String(128))
    finish: Mapped[str] = mapped_column(String(64))                   # "Matte", "Satin", "Dewy · apple of the cheek", ...
    price: Mapped[float] = mapped_column(Numeric(8, 2, asdecimal=False))
    sort: Mapped[int] = mapped_column(Integer, default=0)

    shades: Mapped[list["Shade"]] = relationship(
        back_populates="product", order_by="Shade.sort", cascade="all, delete-orphan"
    )


class Shade(Base):
    __tablename__ = "shades"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(64))
    code: Mapped[str] = mapped_column(String(16))
    hex: Mapped[str] = mapped_column(String(7))
    metallic: Mapped[bool] = mapped_column(Boolean, default=False)
    sort: Mapped[int] = mapped_column(Integer, default=0)

    product: Mapped[Product] = relationship(back_populates="shades")


class ModelPhoto(Base):
    __tablename__ = "model_photos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(64))
    src: Mapped[str] = mapped_column(String(512))                     # URL (frontend /models/... now, S3/CDN later)
    sort: Mapped[int] = mapped_column(Integer, default=0)


def init_db():
    Base.metadata.create_all(engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
