from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from contextlib import asynccontextmanager
import json
import os
from pathlib import Path
from utils.logger import get_app_logger

logger = get_app_logger()

from agents.order_agent import OrderProcessingAgent
from agents.inventory_agent import InventoryAgent
from agents.status_agent import StatusTrackingAgent
from agents.admin_agent import AdminAgent
from agents.inquiry_agent import ProductInquiryAgent

# Import route initializers
from routes.chat import init_chat_routes
from routes.products import init_product_routes
from routes.orders import init_order_routes
from routes.inventory import init_inventory_routes
from routes.admin import init_admin_routes
from routes.users import init_user_routes
from routes.agents import init_agent_routes

# Load environment variables
load_dotenv()
logger.info("Environment variables loaded")

# Data file paths
DATA_DIR = Path(__file__).parent / "data"
PRODUCTS_FILE = DATA_DIR / "products.json"
USERS_FILE = DATA_DIR / "users.json"
ORDERS_FILE = DATA_DIR / "orders.json"


def load_json_data(file_path):
    """Load data from a JSON file"""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            logger.info(f"Loaded {len(data) if isinstance(data, list) else 'data'} from {file_path.name}")
            return data
    except FileNotFoundError:
        logger.warning(f"File not found: {file_path.name}, returning empty list")
        return []
    except json.JSONDecodeError:
        logger.error(f"Failed to decode JSON from {file_path.name}, returning empty list")
        return []


def save_json_data(file_path, data):
    """Save data to a JSON file"""
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        logger.debug(f"Saved data to {file_path.name}")
    except Exception as e:
        logger.error(f"Failed to save data to {file_path.name}: {str(e)}")


def save_all_data():
    """Save all data files"""
    logger.info("Saving all data files...")
    save_json_data(PRODUCTS_FILE, products_data)
    save_json_data(ORDERS_FILE, orders_data)
    logger.info("All data files saved")


# Load initial data
logger.info("Loading initial data...")
products_data = load_json_data(PRODUCTS_FILE)
users_data = load_json_data(USERS_FILE)
orders_data = load_json_data(ORDERS_FILE)
logger.info(f"Data loaded - Products: {len(products_data)}, Users: {len(users_data)}, Orders: {len(orders_data)}")


logger.info("Initializing AI agents...")
order_agent = OrderProcessingAgent(products_data, orders_data)
logger.info("✓ Order Processing Agent initialized")

inventory_agent = InventoryAgent(products_data)
logger.info("✓ Inventory Agent initialized")

status_agent = StatusTrackingAgent(orders_data, users_data)
logger.info("✓ Status Tracking Agent initialized")

admin_agent = AdminAgent(orders_data, products_data, users_data)
logger.info("✓ Admin Agent initialized")

inquiry_agent = ProductInquiryAgent(products_data)
logger.info("✓ Product Inquiry Agent initialized")

logger.info("All agents initialized successfully")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events"""
    logger.info("=== Application Starting ===")
    # Startup code (if needed in the future)
    yield
    # Shutdown: Save all data
    logger.info("=== Application Shutting Down ===")
    logger.info("Saving data before shutdown...")
    save_json_data(PRODUCTS_FILE, products_data)
    save_json_data(USERS_FILE, users_data)
    save_json_data(ORDERS_FILE, orders_data)
    logger.info("Shutdown complete")


app = FastAPI(
    title="Agentic Order Management System",
    description="AI-powered order management with natural language processing",
    version="1.1.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Chat routes (AI-powered)
chat_router = init_chat_routes(
    order_agent, status_agent, inquiry_agent, admin_agent, users_data,
    products_data, orders_data, save_all_data
)
app.include_router(chat_router)

# Product routes
product_router = init_product_routes(products_data)
app.include_router(product_router)

# Order routes
order_router = init_order_routes(orders_data, status_agent, save_all_data)
app.include_router(order_router)

# Inventory routes
inventory_router = init_inventory_routes(inventory_agent, save_all_data)
app.include_router(inventory_router)

# Admin routes
admin_router = init_admin_routes(admin_agent)
app.include_router(admin_router)

# User routes
user_router = init_user_routes(users_data)
app.include_router(user_router)

# Agent info routes
agent_router = init_agent_routes()
app.include_router(agent_router)


@app.get("/", tags=["Root"])
def read_root():
    """Root endpoint"""
    return {
        "message": "Welcome to the Agentic Order Management System",
        "version": "1.1.0",
        "docs": "/docs",
        "endpoints": {
            "chat": "/api/chat",
            "products": "/api/products",
            "orders": "/api/orders",
            "inventory": "/api/inventory",
            "admin": "/api/admin",
            "users": "/api/users",
            "agents": "/api/agents"
        }
    }


@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint"""
    logger.debug("Health check requested")
    return {
        "status": "healthy",
        "products": len(products_data),
        "orders": len(orders_data),
        "users": len(users_data),
        "llm": {
            "model": os.getenv("LLM_MODEL", "gpt-4o"),
            "base_url": os.getenv("LLM_BASE_URL", "")
        }
    }


if __name__ == "__main__":
    import uvicorn

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))

    logger.info(f"Starting server on {host}:{port}")
    logger.info(f"Using LLM model: {os.getenv('LLM_MODEL', 'gpt-4o')}")
    logger.info("Reload mode: enabled")

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True
    )
