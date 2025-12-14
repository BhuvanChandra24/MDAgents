// src/utils/api.js
const BASE = "http://127.0.0.1:8000";

// Create new chat
export async function createNewChatAPI() {
  const res = await fetch(`${BASE}/api/new_chat`, { method: "POST" });
  if (!res.ok) throw new Error("Failed to create chat");
  return await res.json();
}

// List all chats
export async function listChatsAPI() {
  const res = await fetch(`${BASE}/api/list_chats`);
  if (!res.ok) throw new Error("Failed to list chats");
  return await res.json();
}

// Get full chat history
export async function getHistoryAPI(chatId) {
  const res = await fetch(`${BASE}/api/history/${chatId}`);
  if (!res.ok) throw new Error("Failed to load history");
  return await res.json();
}

// Delete chat
export async function deleteHistoryAPI(chatId) {
  const res = await fetch(`${BASE}/api/history/${chatId}`, {
    method: "DELETE",
  });
  if (!res.ok) throw new Error("Failed to delete chat");
  return await res.json();
}

// Send message
export async function sendMessageAPI(payload) {
  const res = await fetch(`${BASE}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!res.ok) throw new Error("Failed to send message");
  return await res.json();
}
