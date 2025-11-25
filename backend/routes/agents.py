from fastapi import APIRouter


def init_agent_routes():
    """Initialize agent information routes"""

    router = APIRouter(prefix="/api/agents", tags=["Agents"])

    @router.get("")
    def get_agents_info():
        """Get information about all AI agents"""
        return {
            "agents": [
                {
                    "type": "order",
                    "name": "Order Processing Agent",
                    "description": "Processes natural language order requests",
                    "capabilities": ["parse orders", "validate products", "create orders"],
                    "status": "active"
                },
                {
                    "type": "inventory",
                    "name": "Inventory Management Agent",
                    "description": "Manages product inventory and stock levels",
                    "capabilities": ["check stock", "update quantities", "suggest alternatives"],
                    "status": "active"
                },
                {
                    "type": "status",
                    "name": "Status Tracking Agent",
                    "description": "Handles order status queries",
                    "capabilities": ["track orders", "provide updates", "answer queries"],
                    "status": "active"
                },
                {
                    "type": "admin",
                    "name": "Administrative Agent",
                    "description": "Provides analytics and system insights",
                    "capabilities": ["generate reports", "identify issues", "analyze trends"],
                    "status": "active"
                }
            ]
        }

    return router
