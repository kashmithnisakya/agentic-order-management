# Agentic Order Management System

An AI-powered order management system that uses natural language processing to handle customer orders and administrative tasks through intelligent agents built with CrewAI.

## Features

- **Natural Language Order Processing**: Customers can place orders using plain English (e.g., "I would like to order 100 units of wireless keyboards")
- **AI-Powered Agents**: Four specialized CrewAI agents handle different aspects of the system
- **Real-time Order Tracking**: Check order status using natural language queries
- **Admin Dashboard**: Comprehensive analytics, order management, and inventory control
- **Inventory Management**: Automatic stock tracking and low-stock alerts
- **RESTful API**: FastAPI backend with automatic documentation

## System Components

### Backend (FastAPI + CrewAI)
- **Order Processing Agent**: Parses natural language orders and creates order records
- **Inventory Agent**: Manages stock levels and suggests alternatives
- **Status Tracking Agent**: Handles order status queries in natural language
- **Admin Agent**: Generates analytics and identifies system issues

### Frontend
- **Client Dashboard**: Natural language order interface for customers
- **Admin Dashboard**: Management interface with analytics and controls

## Architecture

```
Client Dashboard (React)          Admin Dashboard (React)
         |                                   |
         └──────────────┬────────────────────┘
                        │
                   FastAPI Server
                        │
            ┌───────────┼───────────┐
            │           │           │
      Order Agent  Inventory   Status Agent
                    Agent
```

See [ARCHITECTURE.md](./ARCHITECTURE.md) for detailed architecture documentation.

## Prerequisites

- **Python 3.10+**
- **Node.js 18+**
- **OpenAI API Key** (recommended)
  - Get your API key from [https://platform.openai.com](https://platform.openai.com)
  - OR use Ollama for local LLM (free, no API key needed)

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd agentic-order-management
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env

# Edit .env and add your OpenAI API key:
# OPENAI_API_KEY=your_openai_api_key_here  # Required!
# LLM_MODEL=gpt-4o                          # Default model

# Alternative: Use Ollama (free, local)
# Comment out OPENAI_API_KEY and set:
# LLM_MODEL=ollama/llama3.2
# LLM_BASE_URL=http://localhost:11434
# Then run: ollama serve
```

### 3. Client Frontend Setup

```bash
cd client-frontend

# Install dependencies
npm install
```

### 4. Admin Frontend Setup

```bash
cd admin-frontend

# Install dependencies
npm install
```

## Running the Application

You'll need three terminal windows:

### Terminal 1: Backend Server

```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Make sure your .env file has OPENAI_API_KEY set!
python main.py
```

The backend will start on `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/health`

### Terminal 2: Client Frontend

```bash
cd client-frontend
npm run dev
```

The client dashboard will start on `http://localhost:5173`

### Terminal 3: Admin Frontend

```bash
cd admin-frontend
npm run dev
```

The admin dashboard will start on `http://localhost:5174`

## Usage

### Client Dashboard (Customer Interface)

1. **Place an Order**:
   - Navigate to the "Place Order" tab
   - Type your order in natural language
   - Example: "I would like to order 100 units of wireless keyboards"
   - Click "Place Order"
   - The AI agent will process your request and create an order

2. **Check Order Status**:
   - Navigate to the "Check Status" tab
   - Ask about your orders in natural language
   - Example: "Where is my order?" or "What's the status of my recent orders?"
   - The AI agent will provide detailed status information

3. **View Order History**:
   - Navigate to the "Order History" tab
   - See all your past orders with details

### Admin Dashboard

1. **Dashboard Tab**:
   - View comprehensive analytics (total orders, revenue, customers)
   - See order status breakdown
   - Monitor top-selling products
   - Review system alerts and issues

2. **Orders Tab**:
   - View all orders in the system
   - Update order status (pending → processing → shipped → delivered)
   - Monitor order details

3. **Inventory Tab**:
   - View all products and stock levels
   - Adjust inventory quantities
   - Identify low-stock items (highlighted in yellow)

4. **AI Agents Tab**:
   - View all active AI agents
   - See agent capabilities and status
   - Monitor agent performance

## API Endpoints

### Chat (AI-Powered)
- `POST /api/chat/order` - Chat with AI to place an order
- `POST /api/chat/status` - Chat with AI to check order status

### Products
- `GET /api/products` - List all products
- `GET /api/products/{product_id}` - Get specific product

### Orders
- `GET /api/orders` - Get all orders
- `GET /api/orders/user/{user_id}` - Get orders for specific user
- `GET /api/orders/{order_id}` - Get specific order
- `PUT /api/orders/{order_id}/status` - Update order status

### Inventory
- `GET /api/inventory/low-stock` - Get low stock products
- `POST /api/inventory/{product_id}/update` - Update product stock
- `GET /api/inventory/{product_id}/alternatives` - Get alternative products

### Admin & Analytics
- `GET /api/admin/analytics` - Get comprehensive analytics
- `GET /api/admin/trends` - Get order trends
- `GET /api/admin/issues` - Get system issues

### Agents
- `GET /api/agents` - Get information about all AI agents

## Example Natural Language Requests

### Ordering
- "I would like to order 100 units of wireless keyboards"
- "Can I get 50 USB mice?"
- "Order 10 laptop stands please"
- "I need 200 HDMI cables"

### Status Queries
- "Where is my order?"
- "What's the status of my recent orders?"
- "Has my order been shipped?"
- "When will my order arrive?"

## Project Structure

```
agentic-order-management/
├── backend/
│   ├── agents/                  # AI Agent implementations
│   │   ├── order_agent.py       # Order processing agent
│   │   ├── inventory_agent.py   # Inventory management agent
│   │   ├── status_agent.py      # Status tracking agent
│   │   └── admin_agent.py       # Administrative agent
│   ├── routes/                  # API route modules
│   │   ├── __init__.py
│   │   ├── chat.py              # Chat endpoints (AI-powered)
│   │   ├── orders.py            # Order management endpoints
│   │   ├── products.py          # Product endpoints
│   │   ├── inventory.py         # Inventory endpoints
│   │   ├── admin.py             # Admin & analytics endpoints
│   │   ├── users.py             # User endpoints
│   │   └── agents.py            # Agent info endpoints
│   ├── data/
│   │   ├── orders.json          # Order data
│   │   ├── products.json        # Product catalog
│   │   └── users.json           # User data
│   ├── models.py                # Pydantic models
│   ├── main.py                  # FastAPI application (entry point)
│   ├── requirements.txt         # Python dependencies
│   ├── .env.example             # Environment variables template
│   └── .gitignore               # Git ignore rules
├── client-frontend/
│   ├── src/
│   │   ├── App.tsx              # Client dashboard
│   │   └── App.css              # Client styles
│   └── package.json
├── admin-frontend/
│   ├── src/
│   │   ├── App.tsx              # Admin dashboard
│   │   └── App.css              # Admin styles
│   └── package.json
├── ARCHITECTURE.md              # Detailed architecture documentation
├── AI_AGENTS.md                 # AI agent design documentation
├── API.md                       # API reference
├── MIGRATION.md                 # Migration guide
├── CHANGELOG.md                 # Version history
└── README.md                    # This file
```

## AI Agents

### Order Processing Agent
- **Role**: Order Processor
- **Goal**: Accurately parse and process customer orders from natural language
- **Capabilities**:
  - Parse natural language order requests
  - Extract product names and quantities
  - Validate product availability
  - Calculate pricing
  - Create order records

### Inventory Agent
- **Role**: Inventory Manager
- **Goal**: Maintain accurate stock levels
- **Capabilities**:
  - Check product availability
  - Update stock quantities
  - Identify low-stock products
  - Suggest alternative products

### Status Tracking Agent
- **Role**: Status Reporter
- **Goal**: Provide accurate order status information
- **Capabilities**:
  - Parse natural language status queries
  - Retrieve order information
  - Format human-readable responses
  - Provide delivery estimates

### Admin Agent
- **Role**: System Administrator
- **Goal**: Provide insights and analytics
- **Capabilities**:
  - Generate comprehensive analytics
  - Identify operational issues
  - Monitor system performance
  - Analyze trends

## Configuration

### Environment Variables

Create a `.env` file in the `backend` directory:

```env
# OpenAI Configuration (Default)
OPENAI_API_KEY=your_openai_api_key_here
LLM_MODEL=gpt-4o
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=4000

# Alternative Models
# LLM_MODEL=gpt-4o-mini        # Faster, cheaper
# LLM_MODEL=gpt-4-turbo        # More capable
# LLM_MODEL=gpt-3.5-turbo      # Legacy, cheaper

# Server Configuration
HOST=0.0.0.0
PORT=8000
```

### Why OpenAI GPT-4o?

The system uses **OpenAI GPT-4o** by default for best performance:
- **High Quality**: Best-in-class language understanding
- **Reliable**: Consistent, production-ready responses
- **Fast**: Optimized for speed
- **Well-documented**: Extensive documentation and support

**Alternative: Use Ollama (Free & Local)**

If you prefer free, local LLM:
```bash
# 1. Install Ollama from https://ollama.ai
# 2. Pull model: ollama pull llama3.2
# 3. Start server: ollama serve
# 4. Update .env:
#    Comment out OPENAI_API_KEY
#    LLM_MODEL=ollama/llama3.2
#    LLM_BASE_URL=http://localhost:11434
```

### Mock Data

The system uses JSON files for data storage in development:
- `backend/data/products.json` - Product catalog
- `backend/data/users.json` - User accounts
- `backend/data/orders.json` - Order records

## Development

### Adding New Products

Edit `backend/data/products.json`:

```json
{
  "product_id": "prod_009",
  "name": "Product Name",
  "description": "Product description",
  "category": "Category",
  "price": 99.99,
  "stock_quantity": 100,
  "unit": "units"
}
```

### Adding New Users

Edit `backend/data/users.json`:

```json
{
  "user_id": "user_003",
  "name": "User Name",
  "email": "user@example.com",
  "role": "customer",
  "created_at": "2024-01-01T00:00:00Z"
}
```

## Troubleshooting

### Backend won't start
- Ensure Python 3.10+ is installed
- Activate virtual environment
- Install all dependencies: `pip install -r requirements.txt`
- **Check that OPENAI_API_KEY is set in `.env`**
- Verify your API key is valid at [OpenAI Platform](https://platform.openai.com)
- If using Ollama, check that it's running: `ollama serve`

### Frontend won't start
- Ensure Node.js 18+ is installed
- Run `npm install` in the frontend directory
- Check that backend is running on port 8000

### Orders not processing
- **Check Ollama is running**: `ollama list` should show llama3.2
- Check backend logs for errors
- Ensure products exist in `products.json`
- Verify user exists in `users.json`
- Try a different model if current one isn't working well

### CORS errors
- Ensure backend CORS is configured for your frontend ports
- Check that frontend is making requests to correct backend URL

## Production Deployment

For production deployment, consider:

1. **Database**: Replace JSON files with PostgreSQL or MongoDB
2. **Caching**: Add Redis for session management and caching
3. **Message Queue**: Implement RabbitMQ or Kafka for async processing
4. **Authentication**: Add JWT-based authentication
5. **Monitoring**: Implement logging and monitoring (e.g., Sentry, DataDog)
6. **Scaling**: Deploy agents as separate microservices
7. **Security**: Add rate limiting, input validation, API keys

## License

MIT License

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Support

For issues and questions:
- Create an issue in the GitHub repository
- Check existing documentation in `ARCHITECTURE.md` and `AI_AGENTS.md`

## Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- AI agents powered by [CrewAI](https://www.crewai.io/)
- Frontend built with [React](https://react.dev/) and [Vite](https://vitejs.dev/)
