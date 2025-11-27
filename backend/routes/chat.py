from fastapi import APIRouter, HTTPException
from models import NaturalLanguageRequest, NaturalLanguageResponse, StatusQueryRequest, StatusQueryResponse, InquiryRequest, InquiryResponse
from utils.logger import get_route_logger
from pydantic import BaseModel

logger = get_route_logger("chat")


class AdminQueryRequest(BaseModel):
    query: str


class AdminQueryResponse(BaseModel):
    success: bool
    message: str
    data: dict = {}


def init_chat_routes(order_agent, status_agent, inquiry_agent, admin_agent, users_data, products_data, orders_data, save_data_callback):
    """Initialize chat routes with dependencies"""

    router = APIRouter(prefix="/api/chat", tags=["Chat"])

    @router.post("/order", response_model=NaturalLanguageResponse)
    def chat_order(request: NaturalLanguageRequest):
        """
        Chat with AI to place an order using natural language

        Example: "I would like to order 100 units of wireless keyboards"
        """
        logger.info(f"Order chat request received from user: {request.user_id}")
        logger.debug(f"Message: {request.message}")

        try:
            # Validate user exists
            user = next(
                (u for u in users_data if u["user_id"] == request.user_id),
                None
            )
            if not user:
                logger.warning(f"User not found: {request.user_id}")
                raise HTTPException(status_code=404, detail="User not found")

            # Process order using AI agent with chat history
            chat_history = [msg.dict() for msg in request.chat_history] if request.chat_history else []
            logger.debug(f"Processing with {len(chat_history)} history messages")

            result = order_agent.process_order(request.message, request.user_id, chat_history)

            # Save updated data
            if result.get("success"):
                save_data_callback()
                logger.info(f"Order created successfully: {result.get('order_id')}")
            else:
                logger.warning(f"Order creation failed: {result.get('message')}")

            return NaturalLanguageResponse(**result)

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in order chat endpoint: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/status", response_model=StatusQueryResponse)
    def chat_status(request: StatusQueryRequest):
        """
        Chat with AI to check order status using natural language

        Example: "Where is my order?" or "What's the status of my recent orders?"
        """
        logger.info(f"Status query received from user: {request.user_id}")
        logger.debug(f"Query: {request.query}")

        try:
            # Validate user exists
            user = next(
                (u for u in users_data if u["user_id"] == request.user_id),
                None
            )
            if not user:
                logger.warning(f"User not found: {request.user_id}")
                raise HTTPException(status_code=404, detail="User not found")

            # Handle status query using AI agent
            result = status_agent.handle_status_query(request.query, request.user_id)
            logger.info(f"Status query completed. Orders returned: {len(result.get('orders', []))}")

            return StatusQueryResponse(**result)

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in status chat endpoint: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/inquiry", response_model=InquiryResponse)
    def chat_inquiry(request: InquiryRequest):
        """
        Chat with AI to ask about products and availability

        Example: "Do you have wireless keyboards?" or "What products do you have?"
        """
        logger.info("Product inquiry received")
        logger.debug(f"Inquiry: {request.message}")

        try:
            # Process inquiry using AI agent with chat history
            chat_history = [msg.dict() for msg in request.chat_history] if request.chat_history else []
            logger.debug(f"Processing with {len(chat_history)} history messages")

            result = inquiry_agent.handle_inquiry(request.message, chat_history)
            logger.info(f"Inquiry completed. Success: {result.get('success')}")

            return InquiryResponse(**result)

        except Exception as e:
            logger.error(f"Error in inquiry chat endpoint: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/admin", response_model=AdminQueryResponse)
    def chat_admin(request: AdminQueryRequest):
        """
        Chat with AI for admin queries about system-wide data

        Example: "Do we have any orders?" or "What's our revenue?"
        """
        logger.info("Admin query received")
        logger.debug(f"Admin query: {request.query}")

        try:
            # Process admin query using AdminAgent
            result = admin_agent.handle_admin_query(request.query)
            logger.info(f"Admin query completed. Success: {result.get('success')}")
            logger.debug(f"Admin response data: {result.get('data', {})}")

            # Save data if there was a status update or other modification
            if result.get('action') in ['update_order_status']:
                save_data_callback()
                logger.info("Data saved after admin action")

            return AdminQueryResponse(**result)

        except Exception as e:
            logger.error(f"Error in admin chat endpoint: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

    return router
