from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class ItemBase(BaseModel):
    name: str
    description: Optional[str] = None

class ItemCreate(ItemBase):
    pass

class Item(ItemBase):
    id: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class ShopifyCredentials(BaseModel):
    access_token: str
    store_url: str

class Product(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    handle: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    price: Optional[str] = None
    image_url: Optional[str] = None

class OrderItem(BaseModel):
    product_id: Optional[int] = None
    variant_id: Optional[int] = None
    title: str
    quantity: int
    price: float

class Order(BaseModel):
    id: int
    order_number: str
    total_price: float
    created_at: str
    customer_email: Optional[str] = None
    items: List[OrderItem]

class Address(BaseModel):
    address1: Optional[str] = None
    address2: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    province: Optional[str] = None
    zip: Optional[str] = None

class LastOrder(BaseModel):
    items: List[OrderItem]

class Money(BaseModel):
    amount: float
    currency_code: str


class Customer(BaseModel):
    created_at: str
    display_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    tags: List[str]
    product_subscriber_status: Optional[str] = None
    last_order: Optional[LastOrder] = None
    default_address: Optional[Address] = None
    orders: List[Order]
