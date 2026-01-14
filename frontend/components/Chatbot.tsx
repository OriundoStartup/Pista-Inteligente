'use client'

import { useState } from 'react'

export default function Chatbot() {
    const [isOpen, setIsOpen] = useState(false)
    const [messages, setMessages] = useState([
        { text: 'Hola, soy tu asistente de IA. ¿En qué te puedo ayudar hoy?', sender: 'bot' }
    ])
    const [input, setInput] = useState('')

    const sendMessage = async () => {
        if (!input.trim()) return

        const userMessage = input.trim()
        setMessages(prev => [...prev, { text: userMessage, sender: 'user' }])
        setInput('')

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: userMessage })
            })
            const data = await response.json()
            setMessages(prev => [...prev, { text: data.response || 'Sin respuesta', sender: 'bot' }])
        } catch {
            setMessages(prev => [...prev, { text: 'Lo siento, hubo un error al conectar con la IA.', sender: 'bot' }])
        }
    }

    return (
        <>
            {/* Floating Button */}
            <div className="chatbot-fab" onClick={() => setIsOpen(!isOpen)}>
                <img
                    src="/bot_avatar.png"
                    alt="Chat"
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
                        <span>🤖 Asistente Hípico</span>
                    </div>
                    <span style={{ cursor: 'pointer' }} onClick={() => setIsOpen(false)}>✖</span>
                </div>
                <div className="chat-body">
                    {messages.map((msg, i) => (
                        <div key={i} className={`msg ${msg.sender}`}>{msg.text}</div>
                    ))}
                </div>
                <div className="chat-footer">
                    <input
                        type="text"
                        className="chat-input"
                        placeholder="Pregunta sobre una carrera..."
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                    />
                    <button
                        onClick={sendMessage}
                        style={{ padding: '0.5rem', background: 'var(--secondary)', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
                    >
                        ➤
                    </button>
                </div>
            </div>
        </>
    )
}
