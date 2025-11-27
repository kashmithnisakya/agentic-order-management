import { useState, useRef, useEffect } from 'react'
import './ChatPanel.css'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
}

const API_BASE = 'http://localhost:8000/api'

interface ChatPanelProps {
  onDataChange?: () => void
}

export default function ChatPanel({ onDataChange }: ChatPanelProps) {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const sendMessage = async () => {
    if (!input.trim() || loading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setLoading(true)

    try {
      // Use admin endpoint for system-wide queries
      const response = await fetch(`${API_BASE}/chat/admin`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: input
        })
      })

      const data = await response.json()

      // Format message with additional data if available
      let messageContent = data.message || 'I received your request.'

      // If there's a status update confirmation
      if (data.data?.updated_order) {
        const order = data.data.updated_order
        messageContent += `\n\n✅ Updated Order Details:`
        messageContent += `\n- Order ID: ${order.order_id}`
        messageContent += `\n- New Status: ${order.status.toUpperCase()}`
        messageContent += `\n- Total: $${order.total_amount.toFixed(2)}`
        messageContent += `\n- Updated: ${new Date(order.updated_at).toLocaleString()}`
      }

      // If there's inventory data, don't duplicate (already in message)
      // But if there are products in data without message formatting
      if (data.data?.products && data.data.products.length > 0 && !messageContent.includes('📦')) {
        messageContent += '\n\n📦 Inventory:'
        data.data.products.forEach((product: any) => {
          const stockStatus = product.stock_quantity < 100 ? '⚠️ LOW' : '✅'
          messageContent += `\n${stockStatus} ${product.name}: ${product.stock_quantity} units`
        })
      }

      // If there's order data, show summary
      if (data.data?.orders && data.data.orders.length > 0 && !messageContent.includes('Recent Orders')) {
        messageContent += '\n\nRecent Orders:'
        data.data.orders.slice(0, 5).forEach((order: any) => {
          const orderId = order.order_id || 'N/A'
          const status = order.status || 'unknown'
          const amount = order.total_amount !== undefined ? order.total_amount.toFixed(2) : '0.00'
          messageContent += `\n- ${orderId}: ${status.toUpperCase()} - $${amount}`
        })
      }

      // If there are metrics, show key stats (only if not already shown)
      if (data.data?.metrics && !messageContent.includes('System Stats')) {
        const metrics = data.data.metrics
        if (metrics.total_orders > 0) {
          messageContent += `\n\nSystem Stats:`
          messageContent += `\n- Total Orders: ${metrics.total_orders || 0}`
          messageContent += `\n- Revenue: $${(metrics.total_revenue || 0).toFixed(2)}`
          messageContent += `\n- Pending: ${metrics.pending_orders || 0}`
        }
      }

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: messageContent,
        timestamp: new Date()
      }

      setMessages(prev => [...prev, assistantMessage])

      // Notify parent to refresh data if successful
      if (data.success && onDataChange) {
        onDataChange()
      }
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
    <div className="chat-panel">
      <div className="chat-header">
        <h2>AI Assistant</h2>
      </div>

      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="chat-empty">
            <p>Ask me about orders, inventory, or analytics...</p>
            <p style={{ fontSize: '12px', marginTop: '10px', color: '#666' }}>
              Examples:<br/>
              • "Do we have any orders?"<br/>
              • "Check stock availability"<br/>
              • "Change order_abc123 to processing"<br/>
              • "Update order_xyz to shipped"
            </p>
          </div>
        )}
        {messages.map((msg) => (
          <div key={msg.id} className={`message message-${msg.role}`}>
            <div className="message-content">{msg.content}</div>
          </div>
        ))}
        {loading && (
          <div className="message message-assistant">
            <div className="message-content typing">Thinking...</div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input-container">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask about orders, check stock, or update order status..."
          disabled={loading}
          className="chat-input"
        />
        <button
          onClick={sendMessage}
          disabled={loading || !input.trim()}
          className="chat-send-btn"
        >
          Send
        </button>
      </div>
    </div>
  )
}
