import { useState, useEffect } from 'react'
import ChatPanel from './components/ChatPanel'
import './App.css'

// Types
interface Order {
  order_id: string
  user_id: string
  items: Array<{
    product_id: string
    product_name: string
    quantity: number
    unit_price: number
    total_price: number
  }>
  total_amount: number
  status: string
  created_at: string
  updated_at: string
}

interface Product {
  product_id: string
  name: string
  description: string
  category: string
  price: number
  stock_quantity: number
  unit: string
}

interface Analytics {
  total_orders: number
  pending_orders: number
  processing_orders: number
  shipped_orders: number
  delivered_orders: number
  cancelled_orders: number
  total_revenue: number
  total_customers: number
  low_stock_products: Product[]
  top_selling_products: Array<{
    product_id: string
    name: string
    quantity_sold: number
    revenue: number
  }>
  inventory_value: number
}

interface Issue {
  type: string
  severity: string
  message: string
  products?: string[]
  recommendation: string
}

const API_BASE = 'http://localhost:8000/api'

function App() {
  const [analytics, setAnalytics] = useState<Analytics | null>(null)
  const [issues, setIssues] = useState<Issue[]>([])
  const [orders, setOrders] = useState<Order[]>([])

  useEffect(() => {
    fetchAnalytics()
    fetchIssues()
    fetchOrders()
  }, [])

  const fetchOrders = async () => {
    try {
      const res = await fetch(`${API_BASE}/orders`)
      const data = await res.json()
      setOrders(data)
    } catch (error) {
      console.error('Error fetching orders:', error)
    }
  }

  const fetchAnalytics = async () => {
    try {
      const res = await fetch(`${API_BASE}/admin/analytics`)
      const data = await res.json()
      setAnalytics(data)
    } catch (error) {
      console.error('Error fetching analytics:', error)
    }
  }

  const fetchIssues = async () => {
    try {
      const res = await fetch(`${API_BASE}/admin/issues`)
      const data = await res.json()
      setIssues(data.issues || [])
    } catch (error) {
      console.error('Error fetching issues:', error)
    }
  }

  return (
    <div className="app">
      <header className="header">
        <h1>Admin Dashboard</h1>
      </header>

      <main className="main-container">
        <div className="dashboard-section">
          <h2 className="section-title">Analytics Overview</h2>
          {analytics && (
            <div className="metrics-grid">
              <div className="metric-card">
                <div className="metric-label">Total Orders</div>
                <div className="metric-value">{analytics.total_orders}</div>
              </div>
              <div className="metric-card">
                <div className="metric-label">Revenue</div>
                <div className="metric-value">${analytics.total_revenue.toFixed(0)}</div>
              </div>
              <div className="metric-card">
                <div className="metric-label">Pending</div>
                <div className="metric-value">{analytics.pending_orders}</div>
              </div>
              <div className="metric-card">
                <div className="metric-label">Processing</div>
                <div className="metric-value">{analytics.processing_orders}</div>
              </div>
              <div className="metric-card">
                <div className="metric-label">Shipped</div>
                <div className="metric-value">{analytics.shipped_orders}</div>
              </div>
              <div className="metric-card">
                <div className="metric-label">Delivered</div>
                <div className="metric-value">{analytics.delivered_orders}</div>
              </div>
              <div className="metric-card">
                <div className="metric-label">Low Stock Items</div>
                <div className="metric-value">{analytics.low_stock_products.length}</div>
              </div>
              <div className="metric-card">
                <div className="metric-label">Total Customers</div>
                <div className="metric-value">{analytics.total_customers}</div>
              </div>
            </div>
          )}

          {orders.length > 0 && (
            <div className="recent-orders">
              <h3>Recent Orders</h3>
              <div className="orders-list">
                {orders.slice(0, 5).map((order) => (
                  <div key={order.order_id} className="order-item">
                    <div className="order-info">
                      <span className="order-id">{order.order_id}</span>
                      <span className={`order-status status-${order.status}`}>{order.status}</span>
                    </div>
                    <span className="order-amount">${order.total_amount}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {issues.length > 0 && (
            <div className="alerts">
              <h3>System Alerts</h3>
              <div className="alerts-list">
                {issues.map((issue, idx) => (
                  <div key={idx} className={`alert severity-${issue.severity}`}>
                    <div className="alert-message">{issue.message}</div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        <div className="chat-section">
          <ChatPanel />
        </div>
      </main>
    </div>
  )
}

export default App
