'use client'

import { useState, useRef, useEffect } from 'react'

export default function Chatbot() {
    const [isOpen, setIsOpen] = useState(false)
    const [messages, setMessages] = useState([
        { text: '¡Hola! Soy el asistente de Pista Inteligente. 🏇 Pregúntame sobre predicciones, jinetes o cómo funciona nuestro modelo de IA.', sender: 'bot' }
    ])
    const [input, setInput] = useState('')
    const [isLoading, setIsLoading] = useState(false)
    const chatBodyRef = useRef<HTMLDivElement>(null)

    // Auto-scroll al último mensaje
    useEffect(() => {
        if (chatBodyRef.current) {
            chatBodyRef.current.scrollTop = chatBodyRef.current.scrollHeight
        }
    }, [messages])

    const sendMessage = async () => {
        if (!input.trim() || isLoading) return

        const userMessage = input.trim()
        setMessages(prev => [...prev, { text: userMessage, sender: 'user' }])
        setInput('')
        setIsLoading(true)

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: userMessage })
            })

            if (!response.ok) {
                throw new Error('Error en la respuesta del servidor')
            }

            const data = await response.json()
            setMessages(prev => [...prev, { text: data.response || 'Sin respuesta', sender: 'bot' }])
        } catch {
            setMessages(prev => [...prev, {
                text: 'Puedo ayudarte con información sobre predicciones, precisión del modelo, o estadísticas de jinetes. ¿Qué te gustaría saber?',
                sender: 'bot'
            }])
        } finally {
            setIsLoading(false)
        }
    }

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault()
            sendMessage()
        }
    }

    return (
        <>
            {/* Floating Button */}
            <div className="chatbot-fab" onClick={() => setIsOpen(!isOpen)} title="Asistente IA">
                <img
                    src="/bot_avatar.png"
                    alt="Chat"
                    loading="eager"
                    style={{ width: '100%', height: '100%', borderRadius: '50%', objectFit: 'cover' }}
                />
            </div>

            {/* Chat Window */}
            <div className="chatbot-window" style={{ display: isOpen ? 'flex' : 'none' }}>
                <div className="chat-header">
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <img
                            src="/bot_avatar.png"
                            style={{ height: '30px', width: '30px', borderRadius: '50%', border: '1px solid white' }}
                            alt="Bot"
                        />
                        <div>
                            <span style={{ fontWeight: 600 }}>Asistente Hípico</span>
                            <span style={{ fontSize: '0.75rem', opacity: 0.8, display: 'block' }}>
                                {isLoading ? 'Escribiendo...' : 'En línea'}
                            </span>
                        </div>
                    </div>
                    <span style={{ cursor: 'pointer', fontSize: '1.2rem' }} onClick={() => setIsOpen(false)}>✖</span>
                </div>
                <div className="chat-body" ref={chatBodyRef}>
                    {messages.map((msg, i) => (
                        <div key={i} className={`msg ${msg.sender}`}>{msg.text}</div>
                    ))}
                    {isLoading && (
                        <div className="msg bot" style={{ display: 'flex', gap: '4px', padding: '1rem' }}>
                            <span className="typing-dot" style={{ animationDelay: '0ms' }}>•</span>
                            <span className="typing-dot" style={{ animationDelay: '150ms' }}>•</span>
                            <span className="typing-dot" style={{ animationDelay: '300ms' }}>•</span>
                        </div>
                    )}
                </div>
                <div className="chat-footer">
                    <input
                        type="text"
                        className="chat-input"
                        placeholder="Pregunta sobre una carrera..."
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={handleKeyDown}
                        disabled={isLoading}
                    />
                    <button
                        onClick={sendMessage}
                        disabled={isLoading || !input.trim()}
                        style={{
                            padding: '0.5rem 1rem',
                            background: isLoading ? '#666' : 'var(--secondary)',
                            border: 'none',
                            borderRadius: '8px',
                            cursor: isLoading ? 'not-allowed' : 'pointer',
                            color: 'white',
                            fontWeight: 600
                        }}
                    >
                        {isLoading ? '...' : '➤'}
                    </button>
                </div>
            </div>
        </>
    )
}
