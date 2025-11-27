# Backend

FastAPI backend server with AI-powered agents using CrewAI for order management.

## Features

- AI-powered order processing using natural language
- Inventory management with stock tracking
- Order status tracking and queries
- Admin analytics and reporting
- RESTful API with automatic documentation

## Prerequisites

- Python 3.12+
- OpenAI API key

## Installation

### Using uv (Recommended)

[uv](https://docs.astral.sh/uv/) is a fast Python package installer and resolver.

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv pip install -r requirements.txt

# Or sync with pyproject.toml
uv sync
```

## Configuration

Create a `.env` file in the backend directory:

```bash
cp .env.example .env
```

Edit `.env` and add your configuration:

```env
# OpenAI Configuration (Default)
OPENAI_API_KEY=your_openai_api_key_here
LLM_MODEL=gpt-4o
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=4000

# Server Configuration
HOST=0.0.0.0
PORT=8000
```

## Running the Server

### Using uv

```bash
uv run python main.py
```

### Using standard Python

```bash
# Make sure virtual environment is activated
python main.py
```

The server will start on `http://localhost:8000`

## API Documentation

Once the server is running, visit:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **Health Check**: `http://localhost:8000/health`

## Project Structure

```
backend/
├── agents/              # AI agent implementations
│   ├── order_agent.py   # Order processing
│   ├── inventory_agent.py
│   ├── status_agent.py
│   └── admin_agent.py
├── routes/              # API endpoints
├── data/                # JSON data files
│   ├── orders.json
│   ├── products.json
│   └── users.json
├── models.py            # Pydantic models
├── main.py              # Application entry point
└── pyproject.toml       # Project dependencies
```

## Available Endpoints

### Chat Endpoints (AI-Powered)
- `POST /api/chat/order` - Place order using natural language
- `POST /api/chat/status` - Check order status using natural language

### Orders
- `GET /api/orders` - Get all orders
- `GET /api/orders/user/{user_id}` - Get user orders
- `PUT /api/orders/{order_id}/status` - Update order status

### Products & Inventory
- `GET /api/products` - List all products
- `POST /api/inventory/{product_id}/update` - Update stock

### Admin & Analytics
- `GET /api/admin/analytics` - Get system analytics
- `GET /api/admin/issues` - Get system issues

## Troubleshooting

### Server won't start
- Ensure Python 3.12+ is installed
- Check that dependencies are installed
- Verify `.env` file exists with valid OPENAI_API_KEY
- If using Ollama, ensure `ollama serve` is running

### AI agents not responding
- Check your OpenAI API key is valid
- Ensure you have sufficient API credits
- Check backend logs for error messages

## Notes

- The system uses JSON files for data storage (development mode)
- For production, consider using a proper database (PostgreSQL, MongoDB)
- API rate limiting and authentication should be added for production use
