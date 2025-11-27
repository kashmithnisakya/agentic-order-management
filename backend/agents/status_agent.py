from crewai import Agent, Task, Crew, LLM
import json
import os
from datetime import datetime, timezone
from utils.logger import get_agent_logger

logger = get_agent_logger("status_tracking")


class StatusTrackingAgent:
    """
    AI Agent responsible for handling order status queries.

    Thought Process:
    1. Parse natural language status queries
    2. Extract order identifiers or user context
    3. Retrieve relevant order information
    4. Format human-readable status updates
    5. Provide estimated delivery information
    """

    def __init__(self, orders_data, users_data):
        self.orders_data = orders_data
        self.users_data = users_data

        # Configure LLM (OpenAI GPT-4o by default)
        llm = LLM(
            model=os.getenv("LLM_MODEL", "gpt-4o"),
            api_key=os.getenv("OPENAI_API_KEY"),
            temperature=float(os.getenv("LLM_TEMPERATURE", "0.7")),
            max_tokens=int(os.getenv("LLM_MAX_TOKENS", "4000"))
        )

        self.agent = Agent(
            role='Status Reporter',
            goal='Provide accurate and helpful order status information to customers',
            backstory="""You are a customer service expert specializing in order tracking
            and status updates. You have excellent communication skills and can translate
            technical order information into clear, friendly messages that customers can
            easily understand. You're proactive in providing relevant details and setting
            appropriate expectations.""",
            verbose=False,
            allow_delegation=False,
            llm=llm
        )

    def get_user_orders(self, user_id: str):
        """Get all orders for a specific user"""
        user_orders = [
            order for order in self.orders_data
            if order["user_id"] == user_id
        ]
        logger.debug(f"Found {len(user_orders)} orders for user {user_id}")
        return user_orders

    def get_order_by_id(self, order_id: str):
        """Get a specific order by ID"""
        order = next(
            (o for o in self.orders_data if o["order_id"] == order_id),
            None
        )
        return order

    def create_status_query_task(self, query: str, user_id: str):
        """Create a task for the agent to handle status queries"""

        user_orders = self.get_user_orders(user_id)

        if not user_orders:
            orders_summary = "No orders found for this user."
        else:
            orders_summary = "\n".join([
                f"Order {o['order_id']}: Status={o['status']}, "
                f"Total=${o['total_amount']}, Created={o['created_at']}"
                for o in user_orders
            ])

        task_description = f"""
        Handle the following customer status query:

        Customer Query: "{query}"
        Customer ID: {user_id}

        Customer's Orders:
        {orders_summary}

        Your task:
        1. Analyze the customer's query to understand what they're asking about
        2. Determine if they're asking about:
           - A specific order (try to identify which one)
           - A specific product (e.g., "keyboard status" means orders containing keyboards)
           - All their orders
           - General order status
           - Delivery estimates

        3. If they mention a product name (keyboard, mouse, laptop, etc.), find orders containing that product

        4. Provide a helpful, friendly response in JSON format:
        {{
            "success": true,
            "message": "Clear, specific response about their orders. Include order IDs, status, and product details.",
            "order_ids": ["list", "of", "relevant", "order", "ids"],
            "details": "additional helpful information"
        }}

        IMPORTANT:
        - Be conversational and friendly
        - Provide SPECIFIC information: order IDs, product names, quantities, statuses
        - If the customer has orders, show them! Don't just say "visit our website"
        - Include delivery estimates based on status:
          * pending: "Your order will be processed within 1-2 business days"
          * processing: "Your order is being prepared and will ship soon"
          * shipped: "Your order is on the way! Expected delivery in 3-5 business days"
          * delivered: "Your order has been delivered"
        - If no orders found, say "You don't have any orders yet" (not "visit our website")
        """

        task = Task(
            description=task_description,
            agent=self.agent,
            expected_output="JSON formatted status response with customer message"
        )

        return task

    def handle_status_query(self, query: str, user_id: str):
        """
        Handle a natural language status query

        Returns:
            dict: Status information and response message
        """
        logger.info(f"Processing status query for user: {user_id}")
        logger.debug(f"Status query: {query}")

        # Create and execute the task
        task = self.create_status_query_task(query, user_id)
        crew = Crew(
            agents=[self.agent],
            tasks=[task],
            verbose=False
        )

        try:
            logger.debug("Starting AI agent processing for status query...")
            result = crew.kickoff()
            logger.debug(f"Agent result: {result}")

            # Parse the agent's response
            try:
                response_data = json.loads(str(result))
                logger.debug(f"Parsed status response: {response_data}")
            except json.JSONDecodeError:
                logger.warning("Failed to parse JSON from agent response, trying regex extraction")
                # If not valid JSON, try to extract JSON from the text
                import re
                json_match = re.search(r'\{.*\}', str(result), re.DOTALL)
                if json_match:
                    response_data = json.loads(json_match.group())
                    logger.debug(f"Extracted status response: {response_data}")
                else:
                    logger.warning("Could not extract valid JSON, using fallback")
                    # Fallback: provide basic order info
                    user_orders = self.get_user_orders(user_id)
                    return {
                        "success": True,
                        "message": self._generate_basic_status_message(user_orders),
                        "orders": user_orders
                    }

            # Get the relevant orders
            order_ids = response_data.get("order_ids", [])
            logger.debug(f"Relevant order IDs: {order_ids}")
            relevant_orders = [
                self.get_order_by_id(oid) for oid in order_ids
                if self.get_order_by_id(oid)
            ]

            # If no specific orders identified, return all user orders
            if not relevant_orders:
                logger.debug("No specific orders identified, returning all user orders")
                relevant_orders = self.get_user_orders(user_id)

            logger.info(f"Status query completed. Returning {len(relevant_orders)} orders")
            return {
                "success": response_data.get("success", True),
                "message": response_data.get("message", "Here are your orders:"),
                "orders": relevant_orders
            }

        except Exception as e:
            logger.error(f"Error processing status query: {str(e)}", exc_info=True)
            # Fallback to basic functionality
            user_orders = self.get_user_orders(user_id)
            return {
                "success": True,
                "message": self._generate_basic_status_message(user_orders),
                "orders": user_orders
            }

    def _generate_basic_status_message(self, orders):
        """Generate a basic status message when AI agent fails"""
        if not orders:
            return "You don't have any orders yet. Would you like to place an order?"

        if len(orders) == 1:
            order = orders[0]
            items_summary = ", ".join([f"{item['product_name']} (x{item['quantity']})" for item in order.get('items', [])])
            return f"Your order {order['order_id']} is currently {order['status'].upper()}.\n\nItems: {items_summary}\nTotal: ${order['total_amount']}\n\n{'Your order will be processed within 1-2 business days.' if order['status'] == 'pending' else 'Your order is being prepared and will ship soon.'}"

        status_counts = {}
        for order in orders:
            status = order['status']
            status_counts[status] = status_counts.get(status, 0) + 1

        summary = ", ".join([f"{count} {status}" for status, count in status_counts.items()])
        message = f"You have {len(orders)} orders: {summary}.\n\n"
        message += "Recent orders:\n"
        for order in orders[:3]:  # Show last 3 orders
            items = ", ".join([item['product_name'] for item in order.get('items', [])])
            message += f"- {order['order_id']}: {order['status'].upper()} - {items} (${order['total_amount']})\n"
        return message

    def update_order_status(self, order_id: str, new_status: str):
        """Update the status of an order"""
        order = self.get_order_by_id(order_id)

        if not order:
            return {
                "success": False,
                "message": "Order not found"
            }

        valid_statuses = ["pending", "processing", "shipped", "delivered", "cancelled"]
        if new_status not in valid_statuses:
            return {
                "success": False,
                "message": f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
            }

        order["status"] = new_status
        order["updated_at"] = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

        return {
            "success": True,
            "message": f"Order {order_id} status updated to {new_status}",
            "order": order
        }
