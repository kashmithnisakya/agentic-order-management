from crewai import Agent, Task, Crew, LLM
import json
import os
from datetime import datetime, timezone
import uuid
from utils.logger import get_agent_logger

logger = get_agent_logger("order_processing")


class OrderProcessingAgent:
    """
    AI Agent responsible for processing natural language order requests.

    Thought Process:
    1. Parse the natural language input to extract order details
    2. Identify product names and quantities
    3. Validate against available inventory
    4. Calculate pricing
    5. Create order record
    """

    def __init__(self, products_data, orders_data):
        self.products_data = products_data
        self.orders_data = orders_data

        # Configure LLM (OpenAI GPT-4o by default)
        llm = LLM(
            model=os.getenv("LLM_MODEL", "gpt-4o"),
            api_key=os.getenv("OPENAI_API_KEY"),
            temperature=float(os.getenv("LLM_TEMPERATURE", "0.7")),
            max_tokens=int(os.getenv("LLM_MAX_TOKENS", "4000"))
        )

        # Create the Order Processing Agent
        self.agent = Agent(
            role='Order Processor',
            goal='Accurately parse and process customer orders from natural language input',
            backstory="""You are an expert order processing specialist with years of experience
            in understanding customer needs. You excel at interpreting natural language requests
            and converting them into accurate order specifications. You always validate product
            availability and ensure customer satisfaction.""",
            verbose=False,
            allow_delegation=False,
            llm=llm
        )

    def create_order_task(self, user_message: str, user_id: str, chat_history: list = None):
        """Create a task for the agent to process the order"""

        # Build context with available products
        products_list = "\n".join([
            f"- {p['name']} (ID: {p['product_id']}): ${p['price']} each, {p['stock_quantity']} in stock"
            for p in self.products_data
        ])

        # Build chat history context
        chat_context = ""
        if chat_history and len(chat_history) > 0:
            chat_context = "\n\nPrevious Conversation:\n"
            for msg in chat_history[-6:]:  # Last 6 messages (3 exchanges)
                role = msg.get('role', 'user')
                content = msg.get('content', '')
                chat_context += f"{role.upper()}: {content}\n"
            chat_context += "\nIMPORTANT: Use the conversation history above to understand what product the customer is referring to when they use words like 'it', 'that', 'one', etc.\n"

        task_description = f"""
        Process the following customer order request:

        Customer Message: "{user_message}"
        Customer ID: {user_id}
        {chat_context}

        Available Products:
        {products_list}

        Your task:
        1. First, determine if the customer is ACTUALLY TRYING TO PLACE AN ORDER:
           - Ordering phrases: "I want to order", "I need", "Can I buy", "I'd like to purchase"
           - NOT ordering: "Do you have?", "What's available?", "Tell me about", "Show me", just asking questions

        2. If they are NOT placing an order (just asking/inquiring):
           - Return success: false
           - Provide a helpful message directing them to the inquiry endpoint or suggesting they place an order

        3. If they ARE placing an order:
           - Analyze what product(s) they want and quantities
           - Match product names to available products (fuzzy matching OK)
           - Validate sufficient stock
           - Extract order information

        4. Return JSON format:
        {{
            "products": [
                {{
                    "product_id": "...",
                    "product_name": "...",
                    "quantity": number
                }}
            ],
            "success": true/false,
            "message": "human-readable response to customer",
            "error": "error message if any"
        }}

        CRITICAL:
        - Only set success=true and include products if customer is ACTUALLY ORDERING
        - For inquiries/questions, return success=false with helpful message
        - If product not found or out of stock, suggest alternatives
        - Be friendly and professional
        """

        task = Task(
            description=task_description,
            agent=self.agent,
            expected_output="JSON formatted order details with success status and customer message"
        )

        return task

    def process_order(self, user_message: str, user_id: str, chat_history: list = None):
        """
        Process a natural language order request

        Returns:
            dict: Order details including success status, order_id, and message
        """
        logger.info(f"Processing order request for user: {user_id}")
        logger.debug(f"User message: {user_message}")
        logger.debug(f"Chat history length: {len(chat_history) if chat_history else 0}")

        # Create and execute the task
        task = self.create_order_task(user_message, user_id, chat_history)
        crew = Crew(
            agents=[self.agent],
            tasks=[task],
            verbose=False
        )

        try:
            logger.debug("Starting AI agent processing...")
            result = crew.kickoff()
            logger.debug(f"Agent result: {result}")

            # Parse the agent's response
            # The result should be in JSON format
            try:
                order_data = json.loads(str(result))
                logger.debug(f"Parsed order data: {order_data}")
            except json.JSONDecodeError:
                logger.warning("Failed to parse JSON from agent response, trying regex extraction")
                # If not valid JSON, try to extract JSON from the text
                import re
                json_match = re.search(r'\{.*\}', str(result), re.DOTALL)
                if json_match:
                    order_data = json.loads(json_match.group())
                    logger.debug(f"Extracted order data: {order_data}")
                else:
                    logger.error("Could not extract valid JSON from agent response")
                    return {
                        "success": False,
                        "message": "Unable to process order. Please try again.",
                        "error": "Invalid agent response format"
                    }

            if not order_data.get("success"):
                logger.warning(f"Order processing unsuccessful: {order_data.get('message')}")
                return order_data

            # Validate that there are products to order
            if not order_data.get("products") or len(order_data.get("products", [])) == 0:
                logger.warning("No products found in order data - user may be asking a question, not ordering")
                return {
                    "success": False,
                    "message": order_data.get("message", "Please specify which products you'd like to order and the quantity."),
                    "error": "No products specified"
                }

            # Create the order
            order_id = f"order_{uuid.uuid4().hex[:8]}"
            timestamp = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            logger.info(f"Creating order {order_id} for user {user_id}")

            order_items = []
            total_amount = 0.0

            for product_req in order_data.get("products", []):
                # Find the product
                product = next(
                    (p for p in self.products_data if p["product_id"] == product_req["product_id"]),
                    None
                )

                if not product:
                    logger.warning(f"Product {product_req['product_id']} not found in inventory")
                    continue

                quantity = product_req["quantity"]
                unit_price = product["price"]
                item_total = quantity * unit_price

                logger.debug(f"Adding item: {product['name']} x {quantity} = ${item_total}")

                order_items.append({
                    "product_id": product["product_id"],
                    "product_name": product["name"],
                    "quantity": quantity,
                    "unit_price": unit_price,
                    "total_price": item_total
                })

                total_amount += item_total

                # Update stock
                old_stock = product["stock_quantity"]
                product["stock_quantity"] -= quantity
                logger.debug(f"Updated stock for {product['name']}: {old_stock} -> {product['stock_quantity']}")

            # Final validation: Don't create empty orders
            if not order_items or total_amount == 0:
                logger.error("Order validation failed: No valid items or zero total")
                return {
                    "success": False,
                    "message": "Could not create order. Please specify valid products and quantities.",
                    "error": "Empty order or zero total"
                }

            # Create order record
            order = {
                "order_id": order_id,
                "user_id": user_id,
                "items": order_items,
                "total_amount": round(total_amount, 2),
                "status": "pending",
                "created_at": timestamp,
                "updated_at": timestamp
            }

            self.orders_data.append(order)
            logger.info(f"Order {order_id} created successfully. Total: ${round(total_amount, 2)}")

            return {
                "success": True,
                "message": order_data.get("message", "Order processed successfully!"),
                "order_id": order_id,
                "order_details": order
            }

        except Exception as e:
            logger.error(f"Error processing order: {str(e)}", exc_info=True)
            return {
                "success": False,
                "message": "An error occurred while processing your order.",
                "error": str(e)
            }
