// src/components/ChatSidebar.jsx
import React from "react";

export default function ChatSidebar({
  conversations,
  activeId,
  onNewChat,
  onSelectChat,
  onDeleteChat,
}) {
  return (
    <aside className="chat-sidebar">
      <button className="new-chat-btn" onClick={onNewChat}>
        <span>+</span> New Chat
      </button>

      <div className="sidebar-header">
        <div>Recent Chats</div>
      </div>

      <ul className="chat-list">
        {conversations.map((chat) => (
          <li
            key={chat.id}
            className={`chat-item ${chat.id === activeId ? "active" : ""}`}
            onClick={() => onSelectChat(chat.id)}
          >
            <div className="chat-item-content">
              <div className="chat-indicator" />
              <span>{chat.title || "New Chat"}</span>
            </div>

            <button
              className="delete-chat-btn"
              onClick={(e) => {
                e.stopPropagation();
                onDeleteChat(chat.id);
              }}
              title="Delete chat"
            >
              ×
            </button>
          </li>
        ))}
      </ul>

      {conversations.length === 0 && (
        <div style={{ textAlign: "center", padding: "40px 20px", color: "var(--text-secondary)", fontSize: 14 }}>
          No chats yet. Start a conversation!
        </div>
      )}
    </aside>
  );
}
