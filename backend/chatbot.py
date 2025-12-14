# chatbot.py
import os
import sqlite3
import json
import time
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# -----------------------------------
# OpenRouter API
# -----------------------------------
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY missing in .env")

# -----------------------------------
# SQLite DB Setup
# -----------------------------------
DB_PATH = os.getenv("CHAT_DB_PATH", "chat_history.db")

def init_db():
    # Auto-create folder if a custom path is used
    if "/" in DB_PATH:
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id TEXT NOT NULL,
            role TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
    """)

    conn.commit()
    return conn

db = init_db()

# -----------------------------------
# Save & Load Chat History
# -----------------------------------
def save_message(chat_id: str, role: str, message: str):
    cur = db.cursor()
    ts = datetime.utcnow().isoformat() + "Z"

    cur.execute(
        "INSERT INTO messages (chat_id, role, message, created_at) VALUES (?, ?, ?, ?)",
        (chat_id, role, message, ts)
    )

    db.commit()


def get_history(chat_id: str):
    cur = db.cursor()
    cur.execute(
        "SELECT role, message, created_at FROM messages WHERE chat_id = ? ORDER BY id ASC",
        (chat_id,)
    )
    return cur.fetchall()


def delete_history(chat_id: str):
    cur = db.cursor()
    cur.execute("DELETE FROM messages WHERE chat_id = ?", (chat_id,))
    db.commit()


# -----------------------------------
# OpenRouter Wrapper
# -----------------------------------
def call_openrouter(messages, model="deepseek/deepseek-r1"):

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model,
        "messages": messages
    }

    response = requests.post(OPENROUTER_URL, json=payload, headers=headers, timeout=30)
    response.raise_for_status()
    return response.json()


# -----------------------------------
# General Chat Reply (with history)
# -----------------------------------
SYSTEM_PROMPT = (
    "You are a highly intelligent and helpful assistant. "
    "Always answer clearly, concisely, and in well-structured language."
)

def build_conversation(chat_id: str):
    history = get_history(chat_id)

    convo = [{"role": "system", "content": SYSTEM_PROMPT}]

    for role, text, ts in history:
        convo.append({"role": role, "content": text})

    return convo


def general_reply(chat_id: str, user_message: str):

    # Save user's message
    save_message(chat_id, "user", user_message)

    convo = build_conversation(chat_id)
    convo.append({"role": "user", "content": user_message})

    try:
        res = call_openrouter(convo)
        reply = res["choices"][0]["message"]["content"]
    except Exception as e:
        reply = f"Error contacting OpenRouter: {e}"

    # Save assistant reply
    save_message(chat_id, "assistant", reply)

    return reply
