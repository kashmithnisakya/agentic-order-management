from fastapi import APIRouter, HTTPException
from models import Order


def init_order_routes(orders_data, status_agent, save_data_callback):
    """Initialize order routes with dependencies"""

    router = APIRouter(prefix="/api/orders", tags=["Orders"])

    @router.get("", response_model=list[Order])
    def get_all_orders():
        """Get all orders (admin only in production)"""
        return orders_data

    @router.get("/user/{user_id}", response_model=list[Order])
    def get_user_orders(user_id: str):
        """Get all orders for a specific user"""
        user_orders = [o for o in orders_data if o["user_id"] == user_id]
        return user_orders

    @router.get("/{order_id}", response_model=Order)
    def get_order(order_id: str):
        """Get a specific order by ID"""
        order = next(
            (o for o in orders_data if o["order_id"] == order_id),
            None
        )
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        return order

    @router.put("/{order_id}/status")
    def update_order_status(order_id: str, status: str):
        """Update order status (admin only)"""
        result = status_agent.update_order_status(order_id, status)

        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])

        save_data_callback()
        return result

    return router
