from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ItemBase(BaseModel):
    name: str
    description: str
    class Config:
        schema_extra = {
            "example": {
                "name": "Sample Item",
                "description": "A sample item description"
            }
        }

class ItemCreate(ItemBase):
    pass

class Item(ItemBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

class Product(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None

class ShopifyCredentials(BaseModel):
    api_key: str
    password: str
    store_name: str
