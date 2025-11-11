"""
Database Schemas for LONAIRE

Each Pydantic model represents a MongoDB collection. The collection name is the lowercase of the class name.
"""
from typing import List, Optional, Literal
from pydantic import BaseModel, Field, EmailStr

class Collection(BaseModel):
    """Jewelry collections like acciaio, argento, pietre"""
    key: Literal["acciaio", "argento", "pietre"] = Field(..., description="Unique key for the collection")
    name_it: str = Field(..., description="Italian display name")
    name_en: str = Field(..., description="English display name")
    tagline_it: str = Field(..., description="Short poetic tagline (IT)")
    tagline_en: str = Field(..., description="Short poetic tagline (EN)")
    description_it: str = Field(..., description="Description in Italian")
    description_en: str = Field(..., description="Description in English")
    hero_image: Optional[str] = Field(None, description="URL to hero image")

class Product(BaseModel):
    """Individual jewelry pieces"""
    sku: str = Field(..., description="Stock keeping unit")
    title_it: str
    title_en: str
    description_it: Optional[str] = None
    description_en: Optional[str] = None
    material: Literal["acciaio", "argento"] = Field(..., description="Base material")
    stone: Optional[str] = Field(None, description="Stone type, e.g., zircone, perla")
    price: float = Field(..., ge=0)
    available: bool = True
    images: List[str] = Field(default_factory=list)
    collection_key: Literal["acciaio", "argento", "pietre"]

class ContactMessage(BaseModel):
    name: str
    email: EmailStr
    message: str
    language: Literal["it", "en"] = "it"

class NewsletterSubscriber(BaseModel):
    email: EmailStr
    language: Literal["it", "en"] = "it"

# Note: These schemas will be read by the database viewer if enabled, and can be used
# by the API endpoints for validation and persistence.
