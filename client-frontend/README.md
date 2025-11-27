# Client Frontend

Customer dashboard for the Agentic Order Management System. Built with React, TypeScript, and Vite.

## Features

- Place orders using natural language
- Check order status with AI-powered queries
- View order history
- Real-time order tracking

## Prerequisites

- Node.js 18+
- npm

## Installation

```bash
npm install
```

## Running the Application

### Development Mode

```bash
npm run dev
```

The client dashboard will start on `http://localhost:5173`

### Build for Production

```bash
npm run build
```

### Preview Production Build

```bash
npm run preview
```

## Usage

1. Open `http://localhost:5173` in your browser
2. The client dashboard has three tabs:
   - **Place Order**: Submit orders using natural language (e.g., "I would like to order 100 wireless keyboards")
   - **Check Status**: Ask about order status in plain English (e.g., "Where is my order?")
   - **Order History**: View all your past orders

## Example Queries

### Placing Orders
- "I would like to order 100 units of wireless keyboards"
- "Can I get 50 USB mice?"
- "Order 10 laptop stands please"

### Checking Status
- "Where is my order?"
- "What's the status of my recent orders?"
- "Has my order been shipped?"

## Notes

- Make sure the backend server is running on `http://localhost:8000` before starting the client frontend
- The AI agents handle natural language processing, so you can phrase requests naturally
