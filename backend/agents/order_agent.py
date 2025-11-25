from crewai import Agent, Task, Crew, LLM
import json
import os
from datetime import datetime
import uuid


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
            verbose=True,
            allow_delegation=False,
            llm=llm
        )

    def create_order_task(self, user_message: str, user_id: str):
        """Create a task for the agent to process the order"""

        # Build context with available products
        products_list = "\n".join([
            f"- {p['name']} (ID: {p['product_id']}): ${p['price']} each, {p['stock_quantity']} in stock"
            for p in self.products_data
        ])

        task_description = f"""
        Process the following customer order request:

        Customer Message: "{user_message}"
        Customer ID: {user_id}

        Available Products:
        {products_list}

        Your task:
        1. Analyze the customer's message to identify:
           - What product(s) they want to order
           - How many units they need
           - Any special requirements

        2. Match the product name mentioned to our available products (use fuzzy matching if needed)

        3. Validate that we have sufficient stock

        4. Extract the following information in JSON format:
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

        If the product is not found or out of stock, suggest alternatives.
        Be friendly and professional in your response.
        """

        task = Task(
            description=task_description,
            agent=self.agent,
            expected_output="JSON formatted order details with success status and customer message"
        )

        return task

    def process_order(self, user_message: str, user_id: str):
        """
        Process a natural language order request

        Returns:
            dict: Order details including success status, order_id, and message
        """

        # Create and execute the task
        task = self.create_order_task(user_message, user_id)
        crew = Crew(
            agents=[self.agent],
            tasks=[task],
            verbose=True
        )

        try:
            result = crew.kickoff()

            # Parse the agent's response
            # The result should be in JSON format
            try:
                order_data = json.loads(str(result))
            except json.JSONDecodeError:
                # If not valid JSON, try to extract JSON from the text
                import re
                json_match = re.search(r'\{.*\}', str(result), re.DOTALL)
                if json_match:
                    order_data = json.loads(json_match.group())
                else:
                    return {
                        "success": False,
                        "message": "Unable to process order. Please try again.",
                        "error": "Invalid agent response format"
                    }

            if not order_data.get("success"):
                return order_data

            # Create the order
            order_id = f"order_{uuid.uuid4().hex[:8]}"
            timestamp = datetime.now(datetime.UTC).isoformat().replace('+00:00', 'Z')

            order_items = []
            total_amount = 0.0

            for product_req in order_data.get("products", []):
                # Find the product
                product = next(
                    (p for p in self.products_data if p["product_id"] == product_req["product_id"]),
                    None
                )

                if not product:
                    continue

                quantity = product_req["quantity"]
                unit_price = product["price"]
                item_total = quantity * unit_price

                order_items.append({
                    "product_id": product["product_id"],
                    "product_name": product["name"],
                    "quantity": quantity,
                    "unit_price": unit_price,
                    "total_price": item_total
                })

                total_amount += item_total

                # Update stock
                product["stock_quantity"] -= quantity

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

            return {
                "success": True,
                "message": order_data.get("message", "Order processed successfully!"),
                "order_id": order_id,
                "order_details": order
            }

        except Exception as e:
            return {
                "success": False,
                "message": "An error occurred while processing your order.",
                "error": str(e)
            }
