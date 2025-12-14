import React, { useState, useEffect, useRef } from "react";
import ChatSidebar from "./components/ChatSidebar.jsx";
import ChatMessage from "./components/ChatMessage.jsx";
import ChatInput from "./components/ChatInput.jsx";
import jsPDF from "jspdf";

import {
  createNewChatAPI,
  listChatsAPI,
  getHistoryAPI,
  sendMessageAPI,
  deleteHistoryAPI
} from "./utils/api.js";

export default function App() {
  const [loggedIn, setLoggedIn] = useState(
    localStorage.getItem("auth") === "true"
  );

  const [chatList, setChatList] = useState([]);
  const [activeId, setActiveId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);


  // Load conversations on start
  useEffect(() => {
    async function loadChats() {
      try {
        const data = await listChatsAPI();
        setChatList(data.chats || []);

        if (data.chats?.length > 0) {
          setActiveId(data.chats[0].id);
        } else {
          await handleNewChat();
        }
      } catch (err) {
        console.error("Failed to load chats", err);
        await handleNewChat();
      }
    }
    loadChats();
  }, []);

  // Load chat history
  useEffect(() => {
    if (!activeId) return;

    async function loadHistory() {
      try {
        const data = await getHistoryAPI(activeId);

        const formatted = (data.history || []).map(h => ({
          id: h.timestamp,
          role: h.role,
          content: h.message,
          timestamp: h.timestamp
        }));

        setMessages(formatted);
      } catch (err) {
        console.error("History load failed:", err);
        setMessages([]);
      }
    }

    loadHistory();
  }, [activeId]);

  // Auto-scroll
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const handleNewChat = async () => {
    try {
      const data = await createNewChatAPI();

      const newChat = {
        id: data.chat_id,
        title: "New Chat",
        created_at: new Date().toISOString()
      };

      setChatList(prev => [newChat, ...prev]);
      setActiveId(newChat.id);
      setMessages([]);
    } catch (err) {
      console.error("Failed to create chat:", err);
    }
  };

  const handleDeleteChat = async (chatId) => {
    if (!window.confirm("Delete this chat?")) return;

    try {
      await deleteHistoryAPI(chatId);
    } catch (error) {
      console.warn("Backend deletion failed, removing local only");
    }

    setChatList(prev => prev.filter(c => c.id !== chatId));

    if (chatId === activeId) {
      if (chatList.length > 1) {
        const next = chatList.find(c => c.id !== chatId);
        setActiveId(next.id);
      } else {
        await handleNewChat();
      }
    }
  };

  const handleSend = async (text) => {
    if (!text.trim()) return;

    const userMsg = {
      id: Date.now() + "_user",
      role: "user",
      content: text,
      timestamp: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMsg]);
    setLoading(true);

    try {
      const res = await sendMessageAPI({ chat_id: activeId, message: text });

      const botMsg = {
        id: Date.now() + "_bot",
        role: "assistant",
        content: res.reply,
        timestamp: new Date().toISOString(),
      };

      setMessages(prev => [...prev, botMsg]);

      setChatList(prev =>
        prev.map(chat =>
          chat.id === activeId && chat.title === "New Chat"
            ? { ...chat, title: text.slice(0, 40) }
            : chat
        )
      );
    } catch (err) {
      setMessages(prev => [
        ...prev,
        {
          id: Date.now() + "_error",
          role: "assistant",
          content: "Connection error. Try again.",
        },
      ]);
    }

    setLoading(false);
  };

  // EXPORT CHAT TO PDF
  const exportPDF = () => {
    const doc = new jsPDF();
    let y = 10;

    doc.setFontSize(16);
    doc.text("MD Agents Chat Export", 10, y);
    y += 10;

    messages.forEach((msg) => {
      let role = msg.role === "user" ? "User" : "AI";
      let content = `${role}: ${msg.content}`;

      let lines = doc.splitTextToSize(content, 180);
      doc.text(lines, 10, y);
      y += lines.length * 8;

      if (y > 270) {
        doc.addPage();
        y = 10;
      }
    });

    doc.save("chat-history.pdf");
  };

  return (
    <div className="app-root">

      <ChatSidebar
        conversations={chatList}
        activeId={activeId}
        onNewChat={handleNewChat}
        onSelectChat={setActiveId}
        onDeleteChat={handleDeleteChat}
      />

      <main className="chat-main">

        <header className="chat-header">
          <div className="header-content">
            <h1>MD Agents Chat</h1>
            <div className="header-subtitle">
              <span className="status-dot" />
              <span>Smart Medical + General AI Assistant</span>
            </div>
          </div>

          {/* EXPORT PDF BUTTON */}
          <button
            onClick={exportPDF}
            style={{
              marginLeft: "auto",
              padding: "8px 14px",
              background: "var(--primary)",
              border: "none",
              color: "white",
              borderRadius: "6px",
              cursor: "pointer",
            }}
          >
            Export PDF
          </button>
        </header>

        <div className="chat-window">
          {messages.length === 0 ? (
            <div className="welcome-container">
              <div className="welcome-icon">⚕️</div>
              <h1 className="welcome-title">Welcome to MD Agents</h1>
              <p className="welcome-subtitle">
                Ask a medical or general question to begin.
              </p>
            </div>
          ) : (
            <>
              {messages.map(m => (
                <ChatMessage
                  key={m.id}
                  role={m.role}
                  content={m.content}
                  timestamp={m.timestamp}
                />
              ))}
              {loading && (
                <ChatMessage role="assistant" loading={true} content="..." />
              )}
            </>
          )}

          <div ref={messagesEndRef} />
        </div>

        <ChatInput onSend={handleSend} />

      </main>
    </div>
  );
}
