# Admin Frontend

Admin dashboard for the Agentic Order Management System. Built with React, TypeScript, and Vite.

## Features

- View comprehensive analytics (orders, revenue, customers)
- Manage all orders and update their status
- Monitor and adjust inventory levels
- View AI agent information and status

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

The admin dashboard will start on `http://localhost:5174`

### Build for Production

```bash
npm run build
```

### Preview Production Build

```bash
npm run preview
```

## Usage

1. Open `http://localhost:5174` in your browser
2. The admin dashboard has four tabs:
   - **Dashboard**: View analytics and system alerts
   - **Orders**: Manage all orders and update status
   - **Inventory**: Monitor stock levels and adjust quantities
   - **AI Agents**: View active agents and their capabilities

## Notes

- Make sure the backend server is running on `http://localhost:8000` before starting the admin frontend
- The API base URL is configured in the application
