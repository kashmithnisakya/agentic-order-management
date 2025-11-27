# Agentic Order Management System - Architecture

## Design Rationale

This is a proof-of-concept demonstrating a multi-agent AI architecture for order management. The goal is to showcase how specialized AI agents can work together to handle business logic that traditionally requires complex form-based UIs and backend workflows.

### Design Approach

Instead of traditional MVC or microservices, this POC uses a **multi-agent pattern** where each agent is responsible for a specific domain:

- **Order Agent**: Natural language parsing, order validation, and creation
- **Inventory Agent**: Stock management and availability checking
- **Status Agent**: Order status queries and reporting
- **Admin Agent**: Analytics generation and system monitoring

### Key Technical Decisions

1. **Agent Specialization**: Each agent has a single responsibility, making the system modular and testable
2. **Natural Language Interface**: Reduces UI complexity by allowing users to interact conversationally
3. **JSON-based Storage**: Simple data layer for POC - can be swapped for a real database
4. **FastAPI Backend**: Modern, async-capable API framework with automatic documentation
5. **CrewAI Framework**: Handles agent orchestration and inter-agent communication

## System Overview

This is an AI-powered order management system that uses natural language processing to handle customer orders and administrative tasks through intelligent agents built with CrewAI.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend Layer                          │
├──────────────────────────┬──────────────────────────────────┤
│   Client Dashboard       │    Admin Dashboard               │
│   (React + TypeScript)   │    (React + TypeScript)          │
│   - Natural language     │    - Agent management            │
│   - Order placement      │    - Order overview              │
│   - Status tracking      │    - Analytics dashboard         │
└──────────────┬───────────┴────────────┬─────────────────────┘
               │                        │
               └────────────┬───────────┘
                           │ HTTP/REST
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   Backend API Layer                         │
│                  (FastAPI + Python)                         │
├─────────────────────────────────────────────────────────────┤
│  Endpoints:                                                 │
│  - /api/orders/process-natural-language                     │
│  - /api/orders/status                                       │
│  - /api/admin/agents                                        │
│  - /api/products                                            │
└──────────────┬──────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────┐
│               AI Agent Layer (CrewAI)                       │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────────┐  ┌──────────────────┐                 │
│  │ Order Agent      │  │ Inventory Agent   │                │
│  │ - Parse orders   │  │ - Check stock     │                │
│  │ - Validate       │  │ - Update quantity │                │
│  └──────────────────┘  └──────────────────┘                 │
│                                                             │
│  ┌──────────────────┐  ┌──────────────────┐                 │
│  │ Status Agent     │  │ Admin Agent       │                │
│  │ - Track orders   │  │ - Analytics       │                │
│  │ - Updates        │  │ - Management      │                │
│  └──────────────────┘  └──────────────────┘                 │
└──────────────┬──────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────┐
│                    Data Layer                               │
├─────────────────────────────────────────────────────────────┤
│  - Mock JSON databases                                      │
│  - orders.json                                              │
│  - products.json                                            │
│  - users.json                                               │
└─────────────────────────────────────────────────────────────┘
```

## Component Breakdown

### 1. Frontend Layer

#### Client Dashboard
- **Purpose**: Allow customers to interact with the system using natural language
- **Key Features**:
  - Text input for natural language orders
  - Real-time order status tracking
  - Order history view
  - Product catalog browser

#### Admin Dashboard
- **Purpose**: Provide administrative control and monitoring
- **Key Features**:
  - Agent performance monitoring
  - Order management interface
  - Analytics and reporting
  - System configuration

### 2. Backend API Layer

Built with **FastAPI** for high performance and automatic API documentation.

#### Key Endpoints:
- `POST /api/orders/natural-language`: Process natural language order requests
- `GET /api/orders/{order_id}/status`: Get order status
- `GET /api/orders/user/{user_id}`: Get user's orders
- `GET /api/products`: List available products
- `POST /api/admin/agents/create`: Create new AI agent
- `GET /api/admin/analytics`: Get system analytics

### 3. AI Agent Layer (CrewAI)

#### Order Processing Agent
- **Role**: Order Processor
- **Goal**: Accurately parse and process customer orders from natural language
- **Process**:
  1. Receive natural language input
  2. Extract: product name, quantity, user preferences
  3. Validate product availability
  4. Calculate pricing
  5. Create order record

**Example Input**: "I would like to order 100 units of wireless keyboards"

**Agent Thought Process**:
```
1. Identify intent: ORDER_PLACEMENT
2. Extract entities:
   - Product: "wireless keyboards"
   - Quantity: 100
   - Unit: "units"
3. Check inventory via Inventory Agent
4. Validate: quantity <= available_stock
5. Calculate: total_price = quantity * unit_price
6. Create order with status: "pending"
7. Return: order_id, confirmation message
```

#### Inventory Agent
- **Role**: Inventory Manager
- **Goal**: Maintain accurate stock levels and check availability
- **Responsibilities**:
  - Check product availability
  - Update stock quantities
  - Alert on low stock
  - Suggest alternatives when out of stock

#### Status Tracking Agent
- **Role**: Status Reporter
- **Goal**: Provide accurate order status information
- **Capabilities**:
  - Parse natural language status queries
  - Retrieve order details
  - Format human-readable responses
  - Predict delivery estimates

#### Admin Agent
- **Role**: System Administrator
- **Goal**: Provide insights and manage system operations
- **Functions**:
  - Generate analytics reports
  - Monitor agent performance
  - Handle system configurations
  - Alert on anomalies

### 4. Data Layer

Mock JSON-based data storage for development:

#### orders.json
```json
{
  "order_id": "string",
  "user_id": "string",
  "items": [
    {
      "product_id": "string",
      "quantity": "number",
      "unit_price": "number"
    }
  ],
  "total_amount": "number",
  "status": "pending|processing|shipped|delivered",
  "created_at": "timestamp",
  "updated_at": "timestamp"
}
```

#### products.json
```json
{
  "product_id": "string",
  "name": "string",
  "description": "string",
  "category": "string",
  "price": "number",
  "stock_quantity": "number",
  "unit": "string"
}
```

#### users.json
```json
{
  "user_id": "string",
  "name": "string",
  "email": "string",
  "role": "customer|admin",
  "created_at": "timestamp"
}
```

## AI Agent Workflow

### Order Placement Flow

```
Customer Input → Order Agent → Inventory Agent → Database
                     ↓              ↓
                 Parse NL       Check Stock
                     ↓              ↓
                 Extract        Available?
                 Entities           ↓
                     ↓          Yes → Update
                 Validate           ↓
                     ↓          Create Order
                 Response ← Confirmation
```

### Status Check Flow

```
Customer Query → Status Agent → Database
    "Where is        ↓              ↓
    my order?"   Parse Query    Fetch Order
                     ↓              ↓
                 Extract ID     Get Details
                     ↓              ↓
                 Format ← Generate Response
                     ↓
              "Your order is
               currently being
               processed..."
```

## Technology Stack

### Backend
- **Framework**: FastAPI
- **AI Agents**: CrewAI
- **NLP**: OpenAI GPT or local models
- **Data Storage**: JSON files (mock)
- **Language**: Python 3.10+

### Frontend
- **Framework**: React 18
- **Language**: TypeScript
- **UI Library**: Material-UI or Tailwind CSS
- **State Management**: React Context/Redux
- **HTTP Client**: Axios

## Design Decisions & Rationale

### Why CrewAI?
- **Multi-agent collaboration**: Perfect for coordinating multiple specialized agents
- **Role-based design**: Each agent has a specific responsibility
- **Process orchestration**: Built-in task delegation and communication
- **Flexibility**: Easy to add new agents and capabilities

### Why Natural Language Processing?
- **User Experience**: Customers can order in their own words
- **Accessibility**: No complex forms or interfaces needed
- **Flexibility**: Handle variations in order formats
- **Future-proof**: Can be extended with voice input

### Why Mock JSON Data?
- **Rapid Development**: No database setup required
- **Easy Testing**: Simple to modify test data
- **Portability**: Works anywhere Python runs
- **Clear Structure**: Easy to understand data models

## Scalability Considerations

For production deployment:
1. Replace JSON files with PostgreSQL/MongoDB
2. Add Redis for caching and session management
3. Implement message queue (RabbitMQ/Kafka) for async processing
4. Deploy agents as separate microservices
5. Add authentication and authorization
6. Implement rate limiting and monitoring

## Security Considerations

- Input validation on all endpoints
- API key authentication for agent communication
- Rate limiting on order placement
- Sanitization of natural language inputs
- Audit logging for all operations
- Role-based access control (RBAC)

## Error Handling Strategy

### Agent Level
- Retry logic for failed tasks
- Fallback to simpler processing if AI fails
- Clear error messages to users
- Logging for debugging

### API Level
- Structured error responses
- HTTP status codes
- Validation errors with details
- Graceful degradation

## Monitoring & Observability

- Agent performance metrics
- Order processing times
- Success/failure rates
- Natural language parsing accuracy
- System resource usage
- User interaction patterns
