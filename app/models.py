from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from typing import List
from enum import Enum
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
    access_token: str
    store_url: str

class OrderItem(BaseModel):
    product_id: Optional[int] = 0
    variant_id: Optional[int]
    title: str
    quantity: int
    price: float

class Order(BaseModel):
    id: int
    order_number: str | int
    total_price: float
    created_at: datetime
    financial_status: str
    fulfillment_status: Optional[str]
    customer_email: Optional[str]
    items: List[OrderItem]

class OrderStatus(str,Enum):
    ANY = "any"
    OPEN = "open"
    PENDING = "pending"
    INVOICED = "invoiced"
    PAID = "paid"
    PARTIALLY_PAID = "partially_paid"
    UNPAID = "unpaid"
