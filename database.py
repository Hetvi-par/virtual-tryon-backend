import os

from dotenv import load_dotenv
from sqlalchemy import Float, ForeignKey, Integer, String, create_engine
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
    key: Mapped[str] = mapped_column(String(32), unique=True)        # "lips" | "blush" | "eye"
    label: Mapped[str] = mapped_column(String(64))
    color: Mapped[str] = mapped_column(String(7))                     # default shade hex
    opacity: Mapped[float] = mapped_column(Float, default=0.8)
    finish: Mapped[str | None] = mapped_column(String(16), nullable=True)   # only lips have a finish
    sort: Mapped[int] = mapped_column(Integer, default=0)

    shades: Mapped[list["Shade"]] = relationship(
        back_populates="product", order_by="Shade.sort", cascade="all, delete-orphan"
    )


class Shade(Base):
    __tablename__ = "shades"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(64))
    hex: Mapped[str] = mapped_column(String(7))
    sku: Mapped[str | None] = mapped_column(String(64), nullable=True)
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
