from fastapi import APIRouter, HTTPException
from models import NaturalLanguageRequest, NaturalLanguageResponse, StatusQueryRequest, StatusQueryResponse


def init_chat_routes(order_agent, status_agent, users_data, products_data, orders_data, save_data_callback):
    """Initialize chat routes with dependencies"""

    router = APIRouter(prefix="/api/chat", tags=["Chat"])

    @router.post("/order", response_model=NaturalLanguageResponse)
    def chat_order(request: NaturalLanguageRequest):
        """
        Chat with AI to place an order using natural language

        Example: "I would like to order 100 units of wireless keyboards"
        """
        try:
            # Validate user exists
            user = next(
                (u for u in users_data if u["user_id"] == request.user_id),
                None
            )
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            # Process order using AI agent
            result = order_agent.process_order(request.message, request.user_id)

            # Save updated data
            save_data_callback()

            return NaturalLanguageResponse(**result)

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/status", response_model=StatusQueryResponse)
    def chat_status(request: StatusQueryRequest):
        """
        Chat with AI to check order status using natural language

        Example: "Where is my order?" or "What's the status of my recent orders?"
        """
        try:
            # Validate user exists
            user = next(
                (u for u in users_data if u["user_id"] == request.user_id),
                None
            )
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            # Handle status query using AI agent
            result = status_agent.handle_status_query(request.query, request.user_id)

            return StatusQueryResponse(**result)

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return router
