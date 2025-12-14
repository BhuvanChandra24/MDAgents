// src/components/ChatMessage.jsx
import React from "react";

export default function ChatMessage({ role, content, loading, timestamp }) {
  const isUser = role === "user";

  const formatTime = (ts) => {
    if (!ts) return "";
    const d = new Date(ts);
    return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  };

  return (
    <div className={`message-row ${isUser ? "user-row" : "ai-row"}`}>
      <div className="avatar">{isUser ? "👤" : "🤖"}</div>

      <div className={`message-bubble ${isUser ? "user-bubble" : "ai-bubble"}`}>
        {loading ? (
          <div className="typing-indicator">
            <div className="loading-dots">
              <span className="dot" />
              <span className="dot" />
              <span className="dot" />
            </div>
            <div style={{ fontSize: 12, color: "var(--text-secondary)", marginTop: 8 }}>
              MD Agent is thinking...
            </div>
          </div>
        ) : (
          <>
            <div className="message-content">
              {String(content || "").split("\n").map((line, i, arr) => (
                <React.Fragment key={i}>
                  {line}
                  {i < arr.length - 1 && <br />}
                </React.Fragment>
              ))}
            </div>
            {timestamp && <div className="message-timestamp">{formatTime(timestamp)}</div>}
          </>
        )}
      </div>
    </div>
  );
}
