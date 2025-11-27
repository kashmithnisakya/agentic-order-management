from crewai import Agent, Task, Crew, LLM
from datetime import datetime
import json
import os
from utils.logger import get_agent_logger

logger = get_agent_logger("admin")


class AdminAgent:
    """
    AI Agent responsible for administrative tasks and analytics.

    Thought Process:
    1. Generate comprehensive analytics reports
    2. Monitor system performance
    3. Identify trends and anomalies
    4. Provide actionable insights
    """

    def __init__(self, orders_data, products_data, users_data):
        self.orders_data = orders_data
        self.products_data = products_data
        self.users_data = users_data

        # Configure LLM (OpenAI GPT-4o by default)
        llm = LLM(
            model=os.getenv("LLM_MODEL", "gpt-4o"),
            api_key=os.getenv("OPENAI_API_KEY"),
            temperature=float(os.getenv("LLM_TEMPERATURE", "0.7")),
            max_tokens=int(os.getenv("LLM_MAX_TOKENS", "4000"))
        )

        self.agent = Agent(
            role='System Administrator',
            goal='Provide comprehensive analytics and insights for business operations',
            backstory="""You are an experienced business analyst and system administrator
            with expertise in e-commerce operations. You excel at identifying trends,
            spotting potential issues, and providing actionable recommendations to
            improve business performance. You have a keen eye for detail and can
            quickly synthesize complex data into clear insights.""",
            verbose=False,
            allow_delegation=False,
            llm=llm
        )

    def generate_analytics(self):
        """
        Generate comprehensive analytics report

        Returns:
            dict: Analytics data including orders, revenue, and inventory insights
        """

        # Order statistics
        total_orders = len(self.orders_data)
        status_counts = {
            "pending": 0,
            "processing": 0,
            "shipped": 0,
            "delivered": 0,
            "cancelled": 0
        }

        total_revenue = 0.0

        for order in self.orders_data:
            status = order.get("status", "pending")
            status_counts[status] = status_counts.get(status, 0) + 1

            # Count all orders in revenue (including pending)
            total_revenue += order.get("total_amount", 0)

        # Inventory insights
        low_stock_products = [
            p for p in self.products_data
            if p["stock_quantity"] < 100
        ]

        # Customer insights
        total_customers = len([u for u in self.users_data if u["role"] == "customer"])

        # Product performance
        product_sales = {}
        for order in self.orders_data:
            for item in order.get("items", []):
                product_id = item["product_id"]
                quantity = item["quantity"]
                product_sales[product_id] = product_sales.get(product_id, 0) + quantity

        # Top selling products
        top_products = sorted(
            product_sales.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]

        top_products_details = []
        for product_id, quantity_sold in top_products:
            product = next(
                (p for p in self.products_data if p["product_id"] == product_id),
                None
            )
            if product:
                top_products_details.append({
                    "product_id": product_id,
                    "name": product["name"],
                    "quantity_sold": quantity_sold,
                    "revenue": quantity_sold * product["price"]
                })

        return {
            "total_orders": total_orders,
            "pending_orders": status_counts["pending"],
            "processing_orders": status_counts["processing"],
            "shipped_orders": status_counts["shipped"],
            "delivered_orders": status_counts["delivered"],
            "cancelled_orders": status_counts["cancelled"],
            "total_revenue": round(total_revenue, 2),
            "total_customers": total_customers,
            "low_stock_products": low_stock_products,
            "top_selling_products": top_products_details,
            "inventory_value": sum(p["price"] * p["stock_quantity"] for p in self.products_data)
        }

    def get_order_trends(self, days: int = 7):
        """
        Analyze order trends over the specified period

        Returns:
            dict: Trend analysis
        """
        # For now, return basic statistics
        # In production, you'd filter by date range
        return {
            "period_days": days,
            "total_orders": len(self.orders_data),
            "average_order_value": (
                sum(o["total_amount"] for o in self.orders_data) / len(self.orders_data)
                if self.orders_data else 0
            ),
            "trend": "stable"  # Could be: growing, stable, declining
        }

    def identify_issues(self):
        """
        Identify potential operational issues

        Returns:
            list: List of identified issues and recommendations
        """
        issues = []

        # Check for low stock
        low_stock = [p for p in self.products_data if p["stock_quantity"] < 50]
        if low_stock:
            issues.append({
                "type": "inventory",
                "severity": "high" if any(p["stock_quantity"] < 10 for p in low_stock) else "medium",
                "message": f"{len(low_stock)} products have low stock",
                "products": [p["name"] for p in low_stock],
                "recommendation": "Consider reordering these products"
            })

        # Check for stuck orders
        pending_orders = [o for o in self.orders_data if o["status"] == "pending"]
        if len(pending_orders) > 5:
            issues.append({
                "type": "orders",
                "severity": "medium",
                "message": f"{len(pending_orders)} orders are pending processing",
                "recommendation": "Review and process pending orders"
            })

        # Check for out of stock
        out_of_stock = [p for p in self.products_data if p["stock_quantity"] == 0]
        if out_of_stock:
            issues.append({
                "type": "inventory",
                "severity": "high",
                "message": f"{len(out_of_stock)} products are out of stock",
                "products": [p["name"] for p in out_of_stock],
                "recommendation": "Restock these items or mark as unavailable"
            })

        return issues if issues else [{"message": "No issues detected", "type": "info"}]

    def handle_admin_query(self, query: str):
        """
        Handle natural language queries from admin about system status

        Returns:
            dict: Response with relevant information
        """
        logger.info("Processing admin query")
        logger.debug(f"Query: {query}")

        # Build context with current system state
        analytics = self.generate_analytics()

        orders_summary = "\n".join([
            f"Order {o['order_id']}: Status={o['status']}, Total=${o['total_amount']}, User={o['user_id']}"
            for o in self.orders_data[:10]  # Show last 10 orders
        ]) if self.orders_data else "No orders in the system."

        products_summary = "\n".join([
            f"- {p['name']}: {p['stock_quantity']} in stock, ${p['price']} each"
            for p in self.products_data
        ])

        task_description = f"""
        Handle the following admin query:

        Admin Question: "{query}"

        System Overview:
        - Total Orders: {analytics['total_orders']}
        - Pending: {analytics['pending_orders']}
        - Processing: {analytics['processing_orders']}
        - Shipped: {analytics['shipped_orders']}
        - Delivered: {analytics['delivered_orders']}
        - Total Revenue: ${analytics['total_revenue']}
        - Total Customers: {analytics['total_customers']}
        - Low Stock Items: {len(analytics['low_stock_products'])}

        Recent Orders:
        {orders_summary}

        Product Inventory:
        {products_summary}

        Your task:
        1. Analyze the admin's question and determine if it's:
           a) ORDER STATUS UPDATE REQUEST (e.g., "change order_abc to processing", "update order_123 status to shipped")
           b) STOCK/INVENTORY QUERY (e.g., "check stock", "what's in stock", "inventory levels", "stock availability")
           c) GENERAL INFORMATION QUERY (e.g., "how many orders", "show revenue")

        2. For ORDER STATUS UPDATE requests:
           - Extract the order ID and new status
           - Valid statuses: pending, processing, shipped, delivered, cancelled
           - Respond with:
           {{
               "success": true,
               "action": "update_order_status",
               "order_id": "extracted_order_id",
               "new_status": "extracted_status",
               "message": "Order [order_id] status will be updated to [status]"
           }}

        3. For STOCK/INVENTORY queries:
           - Provide detailed inventory information
           - Show products, quantities, and low stock warnings
           - Respond with:
           {{
               "success": true,
               "action": "show_inventory",
               "message": "Here's our current inventory...[list products with stock levels]",
               "data": {{
                   "inventory": "detailed",
                   "low_stock": []
               }}
           }}

        4. For GENERAL queries:
           - Provide relevant information from system data
           - Respond with:
           {{
               "success": true,
               "message": "Clear, informative response with specific data",
               "data": {{
                   "orders": [],
                   "metrics": {{}}
               }}
           }}

        IMPORTANT:
        - Be specific with numbers and details
        - For status updates, extract the exact order ID and status mentioned
        - For inventory, list ALL products with their stock quantities
        - When asked "do we have orders", show total count and recent orders
        """

        task = Task(
            description=task_description,
            agent=self.agent,
            expected_output="JSON formatted response with system information"
        )

        crew = Crew(
            agents=[self.agent],
            tasks=[task],
            verbose=False
        )

        try:
            logger.debug("Starting AI agent processing for admin query...")
            result = crew.kickoff()
            logger.debug(f"Agent result: {result}")

            # Parse the agent's response
            try:
                response_data = json.loads(str(result))
                logger.debug(f"Parsed admin response: {response_data}")
            except json.JSONDecodeError:
                logger.warning("Failed to parse JSON from agent response, trying regex extraction")
                import re
                json_match = re.search(r'\{.*\}', str(result), re.DOTALL)
                if json_match:
                    response_data = json.loads(json_match.group())
                    logger.debug(f"Extracted admin response: {response_data}")
                else:
                    logger.warning("Could not extract valid JSON, using fallback")
                    # Fallback response with actual data
                    return {
                        "success": True,
                        "message": f"We have {analytics['total_orders']} total orders in the system. Recent status: {analytics['pending_orders']} pending, {analytics['processing_orders']} processing, {analytics['delivered_orders']} delivered.",
                        "data": {
                            "orders": self.orders_data[:5],
                            "metrics": analytics
                        }
                    }

            # Check if this is an action request (status update or inventory query)
            action = response_data.get("action")

            if action == "update_order_status":
                # Execute order status update
                order_id = response_data.get("order_id")
                new_status = response_data.get("new_status")

                if order_id and new_status:
                    logger.info(f"Updating order {order_id} to status {new_status}")
                    # Find and update the order
                    order = next((o for o in self.orders_data if o["order_id"] == order_id), None)
                    if order:
                        valid_statuses = ["pending", "processing", "shipped", "delivered", "cancelled"]
                        if new_status.lower() in valid_statuses:
                            order["status"] = new_status.lower()
                            from datetime import datetime, timezone
                            order["updated_at"] = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                            response_data["message"] = f"✅ Order {order_id} status updated to {new_status.upper()} successfully!"
                            response_data["data"] = {"updated_order": order}
                            logger.info(f"Order {order_id} status updated successfully")
                        else:
                            response_data["success"] = False
                            response_data["message"] = f"Invalid status '{new_status}'. Valid statuses: {', '.join(valid_statuses)}"
                            logger.warning(f"Invalid status attempted: {new_status}")
                    else:
                        response_data["success"] = False
                        response_data["message"] = f"Order {order_id} not found"
                        logger.warning(f"Order {order_id} not found")

            elif action == "show_inventory":
                # Add detailed inventory data
                response_data["data"] = {
                    "products": self.products_data,
                    "low_stock": analytics['low_stock_products'],
                    "metrics": analytics
                }
                # Enhance the message with formatted inventory
                inv_msg = "\n\n📦 Current Inventory:\n"
                for p in self.products_data:
                    stock_status = "⚠️ LOW" if p['stock_quantity'] < 100 else "✅"
                    inv_msg += f"{stock_status} {p['name']}: {p['stock_quantity']} units (${p['price']} each)\n"
                response_data["message"] += inv_msg
                logger.info("Inventory data provided to admin")

            else:
                # General query - include standard data
                if "data" not in response_data or not response_data["data"]:
                    response_data["data"] = {}

                response_data["data"]["orders"] = self.orders_data[:5]
                response_data["data"]["metrics"] = analytics

            logger.info(f"Admin query processed successfully. Action: {action or 'general'}")
            return response_data

        except Exception as e:
            logger.error(f"Error processing admin query: {str(e)}", exc_info=True)
            # Return useful fallback data
            return {
                "success": True,
                "message": f"We currently have {analytics['total_orders']} orders in the system with total revenue of ${analytics['total_revenue']}.",
                "data": {
                    "orders": self.orders_data[:5],
                    "metrics": analytics
                }
            }
