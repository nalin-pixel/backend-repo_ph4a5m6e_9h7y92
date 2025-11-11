import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Collection, Product, ContactMessage, NewsletterSubscriber

app = FastAPI(title="LONAIRE API", description="Backend for LONAIRE – Gioielli dal riflesso lunare")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "LONAIRE API is running"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    return response

# ---------------------- API MODELS ----------------------
class Filters(BaseModel):
    material: Optional[str] = None
    stone: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    available: Optional[bool] = None

# ---------------------- COLLECTIONS ----------------------
@app.get("/api/collections", response_model=List[Collection])
def list_collections():
    docs = get_documents("collection")
    # Convert ObjectId to string if present
    for d in docs:
        d.pop("_id", None)
    return docs

@app.post("/api/collections", response_model=dict)
def create_collection(collection: Collection):
    inserted_id = create_document("collection", collection)
    return {"id": inserted_id}

# ---------------------- PRODUCTS ----------------------
@app.get("/api/products", response_model=List[Product])
def list_products(material: Optional[str] = None, stone: Optional[str] = None, min_price: Optional[float] = None, max_price: Optional[float] = None, available: Optional[bool] = None, collection_key: Optional[str] = None):
    filt = {}
    if material:
        filt["material"] = material
    if stone:
        filt["stone"] = stone
    if collection_key:
        filt["collection_key"] = collection_key
    price_filter = {}
    if min_price is not None:
        price_filter["$gte"] = float(min_price)
    if max_price is not None:
        price_filter["$lte"] = float(max_price)
    if price_filter:
        filt["price"] = price_filter
    if available is not None:
        filt["available"] = available

    docs = get_documents("product", filt)
    for d in docs:
        d.pop("_id", None)
    return docs

@app.post("/api/products", response_model=dict)
def create_product(product: Product):
    inserted_id = create_document("product", product)
    return {"id": inserted_id}

# ---------------------- CONTACT ----------------------
@app.post("/api/contact", response_model=dict)
def submit_contact(message: ContactMessage):
    inserted_id = create_document("contactmessage", message)
    return {"id": inserted_id, "status": "received"}

# ---------------------- NEWSLETTER ----------------------
@app.post("/api/newsletter", response_model=dict)
def subscribe_newsletter(sub: NewsletterSubscriber):
    # Prevent duplicates by email
    existing = db["newslettersubscriber"].find_one({"email": sub.email}) if db else None
    if existing:
        return {"status": "already_subscribed"}
    inserted_id = create_document("newslettersubscriber", sub)
    return {"id": inserted_id, "status": "subscribed"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
