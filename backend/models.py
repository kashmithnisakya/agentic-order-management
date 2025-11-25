from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime


class Product(BaseModel):
    product_id: str
    name: str
    description: str
    category: str
    price: float
    stock_quantity: int
    unit: str


class User(BaseModel):
    user_id: str
    name: str
    email: str
    role: Literal["customer", "admin"]
    created_at: str


class OrderItem(BaseModel):
    product_id: str
    product_name: Optional[str] = None
    quantity: int
    unit_price: float
    total_price: Optional[float] = None


class Order(BaseModel):
    order_id: str
    user_id: str
    items: List[OrderItem]
    total_amount: float
    status: Literal["pending", "processing", "shipped", "delivered", "cancelled"]
    created_at: str
    updated_at: str


class NaturalLanguageRequest(BaseModel):
    user_id: str
    message: str


class NaturalLanguageResponse(BaseModel):
    success: bool
    message: str
    order_id: Optional[str] = None
    order_details: Optional[Order] = None
    error: Optional[str] = None


class StatusQueryRequest(BaseModel):
    user_id: str
    query: str  # Natural language query like "where is my order?"


class StatusQueryResponse(BaseModel):
    success: bool
    message: str
    orders: Optional[List[Order]] = None


class AgentConfig(BaseModel):
    agent_type: Literal["order", "inventory", "status", "admin"]
    name: str
    description: str
    enabled: bool = True


class AnalyticsResponse(BaseModel):
    total_orders: int
    pending_orders: int
    processing_orders: int
    shipped_orders: int
    delivered_orders: int
    cancelled_orders: int
    total_revenue: float
    low_stock_products: List[Product]
