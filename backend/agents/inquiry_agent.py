from crewai import Agent, Task, Crew, LLM
import json
import os
from utils.logger import get_agent_logger

logger = get_agent_logger("product_inquiry")


class ProductInquiryAgent:
    """
    AI Agent responsible for handling product inquiries and questions.

    Thought Process:
    1. Parse customer questions about products
    2. Search available inventory
    3. Provide helpful product information
    4. Suggest products and encourage purchases
    5. Answer availability questions
    """

    def __init__(self, products_data):
        self.products_data = products_data

        # Configure LLM (OpenAI GPT-4o by default)
        llm = LLM(
            model=os.getenv("LLM_MODEL", "gpt-4o"),
            api_key=os.getenv("OPENAI_API_KEY"),
            temperature=float(os.getenv("LLM_TEMPERATURE", "0.7")),
            max_tokens=int(os.getenv("LLM_MAX_TOKENS", "4000"))
        )

        self.agent = Agent(
            role='Product Specialist',
            goal='Help customers discover products and provide detailed product information',
            backstory="""You are an enthusiastic product specialist with deep knowledge of
            the inventory. You love helping customers find the perfect products for their needs.
            When customers ask about product availability, you provide detailed information about
            what's in stock, including quantities, prices, and features. You're encouraging and
            always suggest that customers place orders for items they're interested in. You make
            shopping easy and enjoyable.""",
            verbose=False,
            allow_delegation=False,
            llm=llm
        )

    def create_inquiry_task(self, user_message: str, chat_history: list = None):
        """Create a task for the agent to handle product inquiries"""

        # Build context with available products
        products_list = "\n".join([
            f"- {p['name']} (ID: {p['product_id']}): ${p['price']} each, {p['stock_quantity']} {p['unit']} in stock - {p['description']}"
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
            chat_context += "\nIMPORTANT: Use the conversation history to provide contextual responses.\n"

        task_description = f"""
        Handle the following customer product inquiry:

        Customer Question: "{user_message}"
        {chat_context}

        Available Products in Our Inventory:
        {products_list}

        Your task:
        1. Analyze what the customer is asking about
        2. Search through our product inventory to find relevant items
        3. Provide helpful, enthusiastic information about the products
        4. When products are available, mention:
           - Product name and description
           - Current stock quantity
           - Price per unit
           - Encourage them to place an order

        5. Respond in JSON format:
        {{
            "success": true,
            "message": "Friendly, enthusiastic response about the products. If products are available, mention quantities and prices, and encourage ordering.",
            "products_mentioned": [
                {{
                    "product_id": "...",
                    "product_name": "...",
                    "available_quantity": number,
                    "price": number
                }}
            ]
        }}

        IMPORTANT:
        - Be conversational and friendly
        - If the customer asks "do you have X?", respond like "Yes! We have X in stock. We currently have [quantity] units available at $[price] each. Would you like to place an order?"
        - Always encourage customers to order by asking if they'd like to purchase
        - If a product is out of stock, suggest similar alternatives
        - If no matching products found, politely inform them and suggest browsing our catalog
        """

        task = Task(
            description=task_description,
            agent=self.agent,
            expected_output="JSON formatted response with product information and friendly message"
        )

        return task

    def handle_inquiry(self, user_message: str, chat_history: list = None):
        """
        Handle a product inquiry from a customer

        Returns:
            dict: Response with product information
        """
        logger.info(f"Processing product inquiry")
        logger.debug(f"Inquiry message: {user_message}")
        logger.debug(f"Chat history length: {len(chat_history) if chat_history else 0}")

        # Create and execute the task
        task = self.create_inquiry_task(user_message, chat_history)
        crew = Crew(
            agents=[self.agent],
            tasks=[task],
            verbose=False
        )

        try:
            logger.debug("Starting AI agent processing for inquiry...")
            result = crew.kickoff()
            logger.debug(f"Agent result: {result}")

            # Parse the agent's response
            try:
                response_data = json.loads(str(result))
                logger.debug(f"Parsed inquiry response: {response_data}")
            except json.JSONDecodeError:
                logger.warning("Failed to parse JSON from agent response, trying regex extraction")
                # If not valid JSON, try to extract JSON from the text
                import re
                json_match = re.search(r'\{.*\}', str(result), re.DOTALL)
                if json_match:
                    response_data = json.loads(json_match.group())
                    logger.debug(f"Extracted inquiry response: {response_data}")
                else:
                    logger.warning("Could not extract valid JSON, using fallback response")
                    # Fallback response
                    return {
                        "success": True,
                        "message": "I'd be happy to help! Could you please be more specific about which products you're interested in?",
                        "products_mentioned": []
                    }

            logger.info(f"Inquiry processed successfully. Products mentioned: {len(response_data.get('products_mentioned', []))}")
            return response_data

        except Exception as e:
            logger.error(f"Error processing inquiry: {str(e)}", exc_info=True)
            return {
                "success": False,
                "message": "I'm having trouble processing your inquiry. Please try asking again.",
                "error": str(e)
            }

    def search_products(self, keyword: str):
        """
        Search for products matching a keyword

        Returns:
            list: Matching products
        """
        keyword_lower = keyword.lower()
        matching_products = [
            p for p in self.products_data
            if keyword_lower in p['name'].lower() or
            keyword_lower in p['description'].lower() or
            keyword_lower in p['category'].lower()
        ]
        return matching_products

    def get_all_products(self):
        """Get all available products"""
        return self.products_data

    def get_products_by_category(self, category: str):
        """Get products in a specific category"""
        return [
            p for p in self.products_data
            if p['category'].lower() == category.lower()
        ]
