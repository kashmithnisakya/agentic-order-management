from crewai import Agent, LLM
from datetime import datetime
import os


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

            # Only count delivered orders in revenue
            if status in ["delivered", "shipped", "processing"]:
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
