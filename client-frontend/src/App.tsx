import { useState, useEffect } from 'react'
import './App.css'

// Types
interface Product {
  product_id: string
  name: string
  description: string
  category: string
  price: number
  stock_quantity: number
  unit: string
}

interface OrderItem {
  product_id: string
  product_name: string
  quantity: number
  unit_price: number
  total_price: number
}

interface Order {
  order_id: string
  user_id: string
  items: OrderItem[]
  total_amount: number
  status: string
  created_at: string
  updated_at: string
}

const API_BASE = 'http://localhost:8000/api'
const USER_ID = 'user_001' // Demo user

function App() {
  const [message, setMessage] = useState('')
  const [response, setResponse] = useState('')
  const [loading, setLoading] = useState(false)
  const [products, setProducts] = useState<Product[]>([])
  const [orders, setOrders] = useState<Order[]>([])
  const [activeTab, setActiveTab] = useState<'order' | 'status' | 'history'>('order')

  // Fetch products on mount
  useEffect(() => {
    fetchProducts()
    fetchOrders()
  }, [])

  const fetchProducts = async () => {
    try {
      const res = await fetch(`${API_BASE}/products`)
      const data = await res.json()
      setProducts(data)
    } catch (error) {
      console.error('Error fetching products:', error)
    }
  }

  const fetchOrders = async () => {
    try {
      const res = await fetch(`${API_BASE}/orders/user/${USER_ID}`)
      const data = await res.json()
      setOrders(data)
    } catch (error) {
      console.error('Error fetching orders:', error)
    }
  }

  const handlePlaceOrder = async () => {
    if (!message.trim()) {
      setResponse('Please enter an order request')
      return
    }

    setLoading(true)
    setResponse('')

    try {
      const res = await fetch(`${API_BASE}/chat/order`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: USER_ID,
          message: message
        })
      })

      const data = await res.json()

      if (data.success) {
        setResponse(`✓ ${data.message}\n\nOrder ID: ${data.order_id}\nTotal: $${data.order_details?.total_amount || 0}`)
        setMessage('')
        fetchOrders() // Refresh orders
      } else {
        setResponse(`✗ ${data.message || data.error || 'Failed to process order'}`)
      }
    } catch (error) {
      setResponse(`✗ Error: ${error instanceof Error ? error.message : 'Failed to process order'}`)
    } finally {
      setLoading(false)
    }
  }

  const handleStatusQuery = async () => {
    if (!message.trim()) {
      setResponse('Please enter a status query')
      return
    }

    setLoading(true)
    setResponse('')

    try {
      const res = await fetch(`${API_BASE}/chat/status`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: USER_ID,
          query: message
        })
      })

      const data = await res.json()

      if (data.success) {
        let responseText = data.message

        if (data.orders && data.orders.length > 0) {
          responseText += '\n\n'
          data.orders.forEach((order: Order) => {
            responseText += `\n📦 Order ${order.order_id}\n`
            responseText += `   Status: ${order.status}\n`
            responseText += `   Total: $${order.total_amount}\n`
            responseText += `   Date: ${new Date(order.created_at).toLocaleDateString()}\n`
          })
        }

        setResponse(responseText)
        setMessage('')
      } else {
        setResponse(`✗ ${data.message || 'Failed to fetch status'}`)
      }
    } catch (error) {
      setResponse(`✗ Error: ${error instanceof Error ? error.message : 'Failed to fetch status'}`)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      <header className="header">
        <h1>🛒 Order Management System</h1>
        <p>Client Dashboard - Natural Language Ordering</p>
      </header>

      <nav className="tabs">
        <button
          className={activeTab === 'order' ? 'active' : ''}
          onClick={() => setActiveTab('order')}
        >
          Place Order
        </button>
        <button
          className={activeTab === 'status' ? 'active' : ''}
          onClick={() => setActiveTab('status')}
        >
          Check Status
        </button>
        <button
          className={activeTab === 'history' ? 'active' : ''}
          onClick={() => setActiveTab('history')}
        >
          Order History
        </button>
      </nav>

      <main className="main-content">
        {activeTab === 'order' && (
          <div className="section">
            <h2>Place an Order</h2>
            <p className="hint">
              Use natural language! Try: "I would like to order 100 units of wireless keyboards"
            </p>

            <div className="input-group">
              <textarea
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="Type your order request here..."
                rows={4}
                disabled={loading}
              />
              <button
                onClick={handlePlaceOrder}
                disabled={loading}
                className="btn-primary"
              >
                {loading ? 'Processing...' : 'Place Order'}
              </button>
            </div>

            {response && (
              <div className={`response ${response.startsWith('✓') ? 'success' : 'error'}`}>
                <pre>{response}</pre>
              </div>
            )}

            <div className="products-section">
              <h3>Available Products</h3>
              <div className="products-grid">
                {products.map((product) => (
                  <div key={product.product_id} className="product-card">
                    <h4>{product.name}</h4>
                    <p className="description">{product.description}</p>
                    <p className="price">${product.price}</p>
                    <p className="stock">
                      {product.stock_quantity > 0
                        ? `${product.stock_quantity} in stock`
                        : 'Out of stock'}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'status' && (
          <div className="section">
            <h2>Check Order Status</h2>
            <p className="hint">
              Ask about your orders! Try: "Where is my order?" or "What's the status of my orders?"
            </p>

            <div className="input-group">
              <textarea
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="Ask about your order status..."
                rows={3}
                disabled={loading}
              />
              <button
                onClick={handleStatusQuery}
                disabled={loading}
                className="btn-primary"
              >
                {loading ? 'Checking...' : 'Check Status'}
              </button>
            </div>

            {response && (
              <div className="response success">
                <pre>{response}</pre>
              </div>
            )}
          </div>
        )}

        {activeTab === 'history' && (
          <div className="section">
            <h2>Order History</h2>

            {orders.length === 0 ? (
              <p className="empty-state">No orders yet. Place your first order!</p>
            ) : (
              <div className="orders-list">
                {orders.map((order) => (
                  <div key={order.order_id} className="order-card">
                    <div className="order-header">
                      <h3>Order {order.order_id}</h3>
                      <span className={`status status-${order.status}`}>
                        {order.status}
                      </span>
                    </div>

                    <div className="order-items">
                      {order.items.map((item, idx) => (
                        <div key={idx} className="order-item">
                          <span className="item-name">{item.product_name}</span>
                          <span className="item-quantity">Qty: {item.quantity}</span>
                          <span className="item-price">${item.total_price}</span>
                        </div>
                      ))}
                    </div>

                    <div className="order-footer">
                      <span className="order-date">
                        {new Date(order.created_at).toLocaleDateString()}
                      </span>
                      <span className="order-total">
                        Total: ${order.total_amount}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  )
}

export default App
