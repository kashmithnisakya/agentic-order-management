import { useState, useEffect } from 'react'
import './App.css'

// Types
interface Agent {
  type: string
  name: string
  description: string
  capabilities: string[]
  status: string
}

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
  const [activeTab, setActiveTab] = useState<'dashboard' | 'orders' | 'inventory' | 'agents'>('dashboard')
  const [agents, setAgents] = useState<Agent[]>([])
  const [orders, setOrders] = useState<Order[]>([])
  const [products, setProducts] = useState<Product[]>([])
  const [analytics, setAnalytics] = useState<Analytics | null>(null)
  const [issues, setIssues] = useState<Issue[]>([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetchAgents()
    fetchOrders()
    fetchProducts()
    fetchAnalytics()
    fetchIssues()
  }, [])

  const fetchAgents = async () => {
    try {
      const res = await fetch(`${API_BASE}/agents`)
      const data = await res.json()
      setAgents(data.agents || [])
    } catch (error) {
      console.error('Error fetching agents:', error)
    }
  }

  const fetchOrders = async () => {
    try {
      const res = await fetch(`${API_BASE}/orders`)
      const data = await res.json()
      setOrders(data)
    } catch (error) {
      console.error('Error fetching orders:', error)
    }
  }

  const fetchProducts = async () => {
    try {
      const res = await fetch(`${API_BASE}/products`)
      const data = await res.json()
      setProducts(data)
    } catch (error) {
      console.error('Error fetching products:', error)
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

  const updateOrderStatus = async (orderId: string, newStatus: string) => {
    setLoading(true)
    try {
      const res = await fetch(`${API_BASE}/orders/${orderId}/status?status=${newStatus}`, {
        method: 'PUT'
      })
      if (res.ok) {
        fetchOrders()
        fetchAnalytics()
      }
    } catch (error) {
      console.error('Error updating order:', error)
    } finally {
      setLoading(false)
    }
  }

  const updateStock = async (productId: string, change: number) => {
    setLoading(true)
    try {
      const res = await fetch(`${API_BASE}/inventory/${productId}/update?quantity_change=${change}`, {
        method: 'POST'
      })
      if (res.ok) {
        fetchProducts()
        fetchAnalytics()
        fetchIssues()
      }
    } catch (error) {
      console.error('Error updating stock:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      <header className="header">
        <h1>⚙️ Admin Dashboard</h1>
        <p>AI-Powered Order Management System</p>
      </header>

      <nav className="tabs">
        <button
          className={activeTab === 'dashboard' ? 'active' : ''}
          onClick={() => setActiveTab('dashboard')}
        >
          Dashboard
        </button>
        <button
          className={activeTab === 'orders' ? 'active' : ''}
          onClick={() => setActiveTab('orders')}
        >
          Orders
        </button>
        <button
          className={activeTab === 'inventory' ? 'active' : ''}
          onClick={() => setActiveTab('inventory')}
        >
          Inventory
        </button>
        <button
          className={activeTab === 'agents' ? 'active' : ''}
          onClick={() => setActiveTab('agents')}
        >
          AI Agents
        </button>
      </nav>

      <main className="main-content">
        {activeTab === 'dashboard' && analytics && (
          <div className="section">
            <h2>Analytics Overview</h2>

            <div className="stats-grid">
              <div className="stat-card">
                <h3>Total Orders</h3>
                <div className="stat-value">{analytics.total_orders}</div>
              </div>
              <div className="stat-card">
                <h3>Total Revenue</h3>
                <div className="stat-value">${analytics.total_revenue.toFixed(2)}</div>
              </div>
              <div className="stat-card">
                <h3>Customers</h3>
                <div className="stat-value">{analytics.total_customers}</div>
              </div>
              <div className="stat-card">
                <h3>Inventory Value</h3>
                <div className="stat-value">${analytics.inventory_value.toFixed(2)}</div>
              </div>
            </div>

            <div className="row">
              <div className="col">
                <h3>Order Status Breakdown</h3>
                <div className="status-breakdown">
                  <div className="status-item">
                    <span className="label">Pending:</span>
                    <span className="value">{analytics.pending_orders}</span>
                  </div>
                  <div className="status-item">
                    <span className="label">Processing:</span>
                    <span className="value">{analytics.processing_orders}</span>
                  </div>
                  <div className="status-item">
                    <span className="label">Shipped:</span>
                    <span className="value">{analytics.shipped_orders}</span>
                  </div>
                  <div className="status-item">
                    <span className="label">Delivered:</span>
                    <span className="value">{analytics.delivered_orders}</span>
                  </div>
                  <div className="status-item">
                    <span className="label">Cancelled:</span>
                    <span className="value">{analytics.cancelled_orders}</span>
                  </div>
                </div>
              </div>

              {analytics.top_selling_products.length > 0 && (
                <div className="col">
                  <h3>Top Selling Products</h3>
                  <div className="top-products">
                    {analytics.top_selling_products.map((product, idx) => (
                      <div key={product.product_id} className="top-product-item">
                        <span className="rank">#{idx + 1}</span>
                        <span className="name">{product.name}</span>
                        <span className="quantity">{product.quantity_sold} sold</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {issues.length > 0 && (
              <div className="issues-section">
                <h3>⚠️ System Alerts</h3>
                <div className="issues-list">
                  {issues.map((issue, idx) => (
                    <div key={idx} className={`issue-card severity-${issue.severity}`}>
                      <div className="issue-header">
                        <span className="type">{issue.type}</span>
                        <span className="severity">{issue.severity}</span>
                      </div>
                      <p className="message">{issue.message}</p>
                      <p className="recommendation">{issue.recommendation}</p>
                      {issue.products && (
                        <div className="products-affected">
                          Products: {issue.products.join(', ')}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'orders' && (
          <div className="section">
            <h2>Order Management</h2>
            <p className="count">Total: {orders.length} orders</p>

            <div className="orders-table">
              <table>
                <thead>
                  <tr>
                    <th>Order ID</th>
                    <th>User</th>
                    <th>Items</th>
                    <th>Total</th>
                    <th>Status</th>
                    <th>Date</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {orders.map((order) => (
                    <tr key={order.order_id}>
                      <td>{order.order_id}</td>
                      <td>{order.user_id}</td>
                      <td>{order.items.length}</td>
                      <td>${order.total_amount}</td>
                      <td>
                        <span className={`status status-${order.status}`}>
                          {order.status}
                        </span>
                      </td>
                      <td>{new Date(order.created_at).toLocaleDateString()}</td>
                      <td>
                        <select
                          value={order.status}
                          onChange={(e) => updateOrderStatus(order.order_id, e.target.value)}
                          disabled={loading}
                          className="status-select"
                        >
                          <option value="pending">Pending</option>
                          <option value="processing">Processing</option>
                          <option value="shipped">Shipped</option>
                          <option value="delivered">Delivered</option>
                          <option value="cancelled">Cancelled</option>
                        </select>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {activeTab === 'inventory' && (
          <div className="section">
            <h2>Inventory Management</h2>
            <p className="count">Total: {products.length} products</p>

            <div className="products-table">
              <table>
                <thead>
                  <tr>
                    <th>Product</th>
                    <th>Category</th>
                    <th>Price</th>
                    <th>Stock</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {products.map((product) => (
                    <tr key={product.product_id} className={product.stock_quantity < 100 ? 'low-stock' : ''}>
                      <td>
                        <div className="product-info">
                          <strong>{product.name}</strong>
                          <small>{product.description}</small>
                        </div>
                      </td>
                      <td>{product.category}</td>
                      <td>${product.price}</td>
                      <td>
                        <span className={product.stock_quantity < 50 ? 'text-danger' : ''}>
                          {product.stock_quantity} {product.unit}
                        </span>
                      </td>
                      <td>
                        <div className="stock-actions">
                          <button
                            onClick={() => updateStock(product.product_id, -10)}
                            disabled={loading || product.stock_quantity < 10}
                            className="btn-small"
                          >
                            -10
                          </button>
                          <button
                            onClick={() => updateStock(product.product_id, 10)}
                            disabled={loading}
                            className="btn-small"
                          >
                            +10
                          </button>
                          <button
                            onClick={() => updateStock(product.product_id, 100)}
                            disabled={loading}
                            className="btn-small btn-primary"
                          >
                            +100
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {activeTab === 'agents' && (
          <div className="section">
            <h2>AI Agents</h2>
            <p className="hint">
              These AI agents power the order management system using CrewAI
            </p>

            <div className="agents-grid">
              {agents.map((agent) => (
                <div key={agent.type} className="agent-card">
                  <div className="agent-header">
                    <h3>{agent.name}</h3>
                    <span className={`agent-status status-${agent.status}`}>
                      {agent.status}
                    </span>
                  </div>
                  <p className="agent-description">{agent.description}</p>
                  <div className="capabilities">
                    <h4>Capabilities:</h4>
                    <ul>
                      {agent.capabilities.map((cap, idx) => (
                        <li key={idx}>{cap}</li>
                      ))}
                    </ul>
                  </div>
                  <div className="agent-footer">
                    <span className="agent-type">Type: {agent.type}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>
    </div>
  )
}

export default App
