from crewai import Agent, Task, Crew, LLM
import json
import os


class InventoryAgent:
    """
    AI Agent responsible for inventory management and stock validation.

    Thought Process:
    1. Monitor stock levels across all products
    2. Validate product availability for orders
    3. Identify low-stock items
    4. Suggest alternative products when items are unavailable
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
            role='Inventory Manager',
            goal='Maintain accurate stock levels and ensure product availability',
            backstory="""You are a meticulous inventory specialist with expertise in
            stock management and supply chain operations. You always ensure accurate
            stock tracking and proactively identify potential stock issues before
            they become problems. You're great at suggesting alternatives when
            products are unavailable.""",
            verbose=False,
            allow_delegation=False,
            llm=llm
        )

    def check_stock(self, product_id: str, requested_quantity: int):
        """
        Check if sufficient stock is available for a product

        Returns:
            dict: Availability status and details
        """
        product = next(
            (p for p in self.products_data if p["product_id"] == product_id),
            None
        )

        if not product:
            return {
                "available": False,
                "reason": "Product not found",
                "product": None
            }

        if product["stock_quantity"] < requested_quantity:
            return {
                "available": False,
                "reason": f"Insufficient stock. Available: {product['stock_quantity']}, Requested: {requested_quantity}",
                "product": product,
                "available_quantity": product["stock_quantity"]
            }

        return {
            "available": True,
            "product": product,
            "available_quantity": product["stock_quantity"]
        }

    def get_low_stock_products(self, threshold: int = 100):
        """
        Identify products with stock below the threshold

        Returns:
            list: Products with low stock
        """
        low_stock = [
            p for p in self.products_data
            if p["stock_quantity"] < threshold
        ]

        return low_stock

    def suggest_alternatives(self, product_id: str):
        """
        Suggest alternative products from the same category

        Returns:
            list: Alternative products
        """
        original_product = next(
            (p for p in self.products_data if p["product_id"] == product_id),
            None
        )

        if not original_product:
            return []

        alternatives = [
            p for p in self.products_data
            if p["category"] == original_product["category"]
            and p["product_id"] != product_id
            and p["stock_quantity"] > 0
        ]

        return alternatives[:3]  # Return top 3 alternatives

    def update_stock(self, product_id: str, quantity_change: int):
        """
        Update stock quantity for a product

        Args:
            product_id: Product identifier
            quantity_change: Positive for restocking, negative for sales

        Returns:
            dict: Updated product information
        """
        product = next(
            (p for p in self.products_data if p["product_id"] == product_id),
            None
        )

        if not product:
            return {
                "success": False,
                "message": "Product not found"
            }

        new_quantity = product["stock_quantity"] + quantity_change

        if new_quantity < 0:
            return {
                "success": False,
                "message": "Cannot reduce stock below zero"
            }

        product["stock_quantity"] = new_quantity

        return {
            "success": True,
            "message": f"Stock updated for {product['name']}",
            "product": product
        }
