import os
import re
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from database import ModelPhoto, Product, Shade, get_db, init_db

HEX = re.compile(r"^#[0-9a-fA-F]{6}$")


# ---------- Schemas ----------
class ShadeOut(BaseModel):
    id: int
    name: str
    code: str
    hex: str
    metallic: bool = False
    lash: dict | None = None

    model_config = {"from_attributes": True}


class ProductOut(BaseModel):
    id: str = Field(validation_alias="slug")
    type: str
    name: str
    finish: str
    price: float
    defaults: dict[str, str] | None = None
    shades: list[ShadeOut]

    model_config = {"from_attributes": True}


class ModelPhotoOut(BaseModel):
    name: str
    src: str

    model_config = {"from_attributes": True}


class ShadeIn(BaseModel):
    name: str
    code: str
    hex: str
    metallic: bool = False
    lash: dict | None = None

    @field_validator("hex")
    @classmethod
    def valid_hex(cls, v: str) -> str:
        if not HEX.match(v):
            raise ValueError("hex must look like #a1b2c3")
        return v.lower()


# ---------- App ----------
@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title="Virtual Try-On API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:5173").split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/products", response_model=list[ProductOut])
def list_products(db: Session = Depends(get_db)):
    stmt = select(Product).options(selectinload(Product.shades)).order_by(Product.sort)
    return db.scalars(stmt).all()


@app.post("/api/products/{slug}/shades", response_model=ShadeOut, status_code=201)
def add_shade(slug: str, body: ShadeIn, db: Session = Depends(get_db)):
    product = db.scalar(select(Product).where(Product.slug == slug))
    if not product:
        raise HTTPException(404, f"Unknown product '{slug}'")
    shade = Shade(product=product, name=body.name, code=body.code, hex=body.hex, metallic=body.metallic, lash=body.lash, sort=len(product.shades))
    db.add(shade)
    db.commit()
    return shade


@app.delete("/api/shades/{shade_id}", status_code=204)
def delete_shade(shade_id: int, db: Session = Depends(get_db)):
    shade = db.get(Shade, shade_id)
    if not shade:
        raise HTTPException(404, "Shade not found")
    db.delete(shade)
    db.commit()


@app.get("/api/model-photos", response_model=list[ModelPhotoOut])
def list_model_photos(db: Session = Depends(get_db)):
    return db.scalars(select(ModelPhoto).order_by(ModelPhoto.sort)).all()
