import { useState, useRef, useEffect } from 'react'
import './App.css'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
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

const API_BASE = 'http://localhost:8000/api'
const USER_ID = 'user_001'

function App() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [products, setProducts] = useState<Product[]>([])
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    fetchProducts()
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

  const sendMessage = async () => {
    if (!input.trim() || loading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    const currentInput = input
    setInput('')
    setLoading(true)

    try {
      const lowerInput = currentInput.toLowerCase()
      let assistantContent = ''

      // Prepare chat history (convert messages to chat history format)
      const chatHistory = messages.map(msg => ({
        role: msg.role,
        content: msg.content
      }))

      // Check if it's a status query (expanded keywords)
      if (lowerInput.includes('status') ||
          lowerInput.includes('where is') ||
          lowerInput.includes('where are') ||
          lowerInput.includes('track') ||
          lowerInput.includes('my order') ||
          lowerInput.includes('order status') ||
          lowerInput.includes('keyboard status') ||
          lowerInput.includes('mouse status') ||
          lowerInput.includes('check order') ||
          lowerInput.includes('check my') ||
          (lowerInput.includes('order') && lowerInput.includes('?')) ||
          (lowerInput.includes('my') && (lowerInput.includes('keyboard') || lowerInput.includes('mouse') || lowerInput.includes('laptop')) && lowerInput.includes('?'))) {
        try {
          const statusResponse = await fetch(`${API_BASE}/chat/status`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              user_id: USER_ID,
              query: currentInput
            })
          })
          const statusData = await statusResponse.json()
          assistantContent = statusData.message

          // Add order details if available
          if (statusData.orders && statusData.orders.length > 0) {
            assistantContent += '\n\nYour Orders:\n'
            statusData.orders.forEach((order: any) => {
              assistantContent += `\n📦 Order ${order.order_id}`
              assistantContent += `\n   Status: ${order.status.toUpperCase()}`
              assistantContent += `\n   Total: $${order.total_amount}`
              assistantContent += `\n   Items:`
              order.items.forEach((item: any) => {
                assistantContent += `\n   - ${item.product_name} x ${item.quantity}`
              })
              assistantContent += `\n`
            })
          }
        } catch (error) {
          assistantContent = 'Sorry, I could not check your order status. Please try again.'
        }
      }
      // Check if it's a product inquiry (asking about availability, products)
      else if (lowerInput.includes('do you have') ||
               lowerInput.includes('have you got') ||
               lowerInput.includes('is there') ||
               lowerInput.includes('are there') ||
               lowerInput.includes('what products') ||
               lowerInput.includes('show me') ||
               lowerInput.includes('available') ||
               lowerInput.includes('in stock') ||
               (lowerInput.includes('?') && !lowerInput.includes('order'))) {
        try {
          const inquiryResponse = await fetch(`${API_BASE}/chat/inquiry`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              message: currentInput,
              chat_history: chatHistory
            })
          })
          const inquiryData = await inquiryResponse.json()
          assistantContent = inquiryData.message

          // Add product details if mentioned
          if (inquiryData.products_mentioned && inquiryData.products_mentioned.length > 0) {
            assistantContent += '\n\n'
            inquiryData.products_mentioned.forEach((product: any) => {
              assistantContent += `\n${product.product_name}: ${product.available_quantity} units at $${product.price} each`
            })
          }
        } catch (error) {
          assistantContent = 'Sorry, I could not process your inquiry. Please try again.'
        }
      }
      // Otherwise, try to process as an order
      else {
        try {
          const orderResponse = await fetch(`${API_BASE}/chat/order`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              user_id: USER_ID,
              message: currentInput,
              chat_history: chatHistory
            })
          })

          const orderData = await orderResponse.json()

          if (orderData.success) {
            assistantContent = `${orderData.message}\n\n`
            if (orderData.order_id) {
              assistantContent += `Order ID: ${orderData.order_id}\n`
            }
            if (orderData.order_details?.total_amount) {
              assistantContent += `Total Amount: $${orderData.order_details.total_amount}\n`
            }
            if (orderData.order_details?.items) {
              assistantContent += '\nItems:\n'
              orderData.order_details.items.forEach((item: any) => {
                assistantContent += `- ${item.product_name} x ${item.quantity} = $${item.total_price}\n`
              })
            }

            // Refresh product list to show updated stock quantities
            fetchProducts()
          } else {
            assistantContent = orderData.message || orderData.error || 'Sorry, I could not process your order.'
          }
        } catch (error) {
          assistantContent = 'Sorry, I encountered an error processing your order. Please try again.'
        }
      }

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: assistantContent,
        timestamp: new Date()
      }

      setMessages(prev => [...prev, assistantMessage])
    } catch (error) {
      console.error('Error sending message:', error)
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setLoading(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  return (
    <div className="app">
      <header className="header">
        <h1>Customer Portal</h1>
      </header>

      <div className="main-layout">
        <aside className="products-sidebar">
          <h2>Available Products</h2>
          <div className="products-list">
            {products.length === 0 ? (
              <div className="loading-state">
                <p>Loading products...</p>
              </div>
            ) : (
              products.map((product) => (
                <div key={product.product_id} className="product-card">
                  <h3>{product.name}</h3>
                  <p className="product-description">{product.description}</p>
                  <div className="product-details">
                    <span className="product-price">${product.price}</span>
                    <span className="product-stock">
                      {product.stock_quantity} {product.unit} in stock
                    </span>
                  </div>
                  <span className="product-category">{product.category}</span>
                </div>
              ))
            )}
          </div>
        </aside>

        <main className="chat-container">
        <div className="chat-header">
          <h2>Order Assistant</h2>
          <p>Ask me to place orders, check status, or answer questions!</p>
        </div>

        <div className="chat-messages">
          {messages.length === 0 && (
            <div className="welcome-message">
              <h3>Welcome!</h3>
              <p>I can help you with:</p>
              <ul>
                <li>Place orders using natural language</li>
                <li>Check order status</li>
                <li>View order history</li>
                <li>Answer questions about products</li>
              </ul>
              <p className="example">Try: "I need 50 wireless keyboards" or "Where is my order?"</p>
            </div>
          )}

          {messages.map((msg) => (
            <div key={msg.id} className={`message message-${msg.role}`}>
              <div className="message-content">
                {msg.content.split('\n').map((line, i) => (
                  <p key={i}>{line || '\u00A0'}</p>
                ))}
              </div>
              <div className="message-time">
                {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </div>
            </div>
          ))}

          {loading && (
            <div className="message message-assistant">
              <div className="message-content typing">
                <div className="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        <div className="chat-input-area">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type your message here..."
            disabled={loading}
            className="chat-input"
          />
          <button
            onClick={sendMessage}
            disabled={loading || !input.trim()}
            className="send-button"
          >
            Send
          </button>
        </div>
      </main>
      </div>
    </div>
  )
}

export default App
