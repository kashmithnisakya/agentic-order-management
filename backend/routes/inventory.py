from fastapi import APIRouter, HTTPException


def init_inventory_routes(inventory_agent, save_data_callback):
    """Initialize inventory routes with dependencies"""

    router = APIRouter(prefix="/api/inventory", tags=["Inventory"])

    @router.get("/low-stock")
    def get_low_stock_products(threshold: int = 100):
        """Get products with low stock"""
        low_stock = inventory_agent.get_low_stock_products(threshold)
        return {"low_stock_products": low_stock, "count": len(low_stock)}

    @router.post("/{product_id}/update")
    def update_product_stock(product_id: str, quantity_change: int):
        """Update product stock (admin only)"""
        result = inventory_agent.update_stock(product_id, quantity_change)

        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])

        save_data_callback()
        return result

    @router.get("/{product_id}/alternatives")
    def get_product_alternatives(product_id: str):
        """Get alternative products"""
        alternatives = inventory_agent.suggest_alternatives(product_id)
        return {"alternatives": alternatives}

    return router
