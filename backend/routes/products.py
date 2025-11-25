from fastapi import APIRouter, HTTPException
from models import Product


def init_product_routes(products_data):
    """Initialize product routes with dependencies"""

    router = APIRouter(prefix="/api/products", tags=["Products"])

    @router.get("", response_model=list[Product])
    def get_products():
        """Get all available products"""
        return products_data

    @router.get("/{product_id}", response_model=Product)
    def get_product(product_id: str):
        """Get a specific product by ID"""
        product = next(
            (p for p in products_data if p["product_id"] == product_id),
            None
        )
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return product

    return router
