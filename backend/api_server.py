# api_server.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from litellm.exceptions import APIError
import uuid
import traceback
import chatbot
from crew_runner import run_mdagents

app = FastAPI(title="Chatbot API with History")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------
# Helpers
# --------------------------
def get_db_conn():
    """
    Automatically find the correct DB variable used inside chatbot.py.
    Supports db, _db_conn, conn.
    """
    for name in ["_db_conn", "db", "conn"]:
        if hasattr(chatbot, name):
            return getattr(chatbot, name)

    raise RuntimeError(
        "No database connection found in chatbot.py. "
        "Expected one of: _db_conn, db, conn"
    )

# --------------------------
# Models
# --------------------------
class ChatRequest(BaseModel):
    chat_id: str
    message: str

class ChatResponse(BaseModel):
    reply: str
    is_medical: bool

# --------------------------
# Medical Keyword Detection
# --------------------------
def is_medical(msg: str):
    keywords = [
        "pain", "fever", "infection", "diagnose", "treatment", "sepsis",
        "scan", "mri", "ct", "injury", "cancer", "stroke"
    ]
    msg = msg.lower()
    return any(k in msg for k in keywords)

# --------------------------
# Create New Chat
# --------------------------
@app.post("/api/new_chat")
def create_new_chat():
    chat_id = str(uuid.uuid4())
    return {"chat_id": chat_id}

# --------------------------
# List All Chats (Sidebar)
# --------------------------
@app.get("/api/list_chats")
def list_chats():
    try:
        conn = get_db_conn()
        cur = conn.cursor()

        cur.execute("SELECT DISTINCT chat_id FROM messages ORDER BY id DESC")
        rows = cur.fetchall()

        chats = []
        for (chat_id,) in rows:
            cur.execute("""
                SELECT message FROM messages 
                WHERE chat_id = ? AND role = 'user'
                ORDER BY id ASC LIMIT 1
            """, (chat_id,))
            row = cur.fetchone()
            title = row[0][:50] if row else "New Chat"

            chats.append({"id": chat_id, "title": title})

        return {"chats": chats}

    except Exception as e:
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

# --------------------------
# Chat Endpoint (Medical + General)
# --------------------------
@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    chat_id = req.chat_id
    msg = req.message.strip()

    if not msg:
        raise HTTPException(400, "Message cannot be empty.")

    # MEDICAL MODE
    if is_medical(msg):
        chatbot.save_message(chat_id, "user", msg)

        try:
            result = run_mdagents(msg)

            reasoning = "\n".join(f"- {r}" for r in result.get("reasoning", []))
            final = result.get("final", "No final output provided.")
            complexity = result.get("complexity", "Unknown")

            reply = (
                f"Medical Reasoning (Educational Only)\n\n"
                f"Complexity: {complexity}\n\n"
                f"Reasoning:\n{reasoning}\n\n"
                f"Final Opinion:\n{final}\n\n"
                "⚠ Not a substitute for real medical advice."
            )

        except APIError:
            # OpenRouter / token / credit issue
            reply = (
                "⚠ Medical AI service is temporarily unavailable due to usage limits.\n\n"
                "Please try again later."
            )

        except Exception:
            # Any unexpected error
            traceback.print_exc()
            reply = "⚠ An internal error occurred while processing the medical query."

        chatbot.save_message(chat_id, "assistant", reply)
        return ChatResponse(reply=reply, is_medical=True)

    # GENERAL CHAT MODE
    reply = chatbot.general_reply(chat_id, msg)
    return ChatResponse(reply=reply, is_medical=False)

# --------------------------
# Get chat history
# --------------------------
@app.get("/api/history/{chat_id}")
def get_chat_history(chat_id: str):
    history = chatbot.get_history(chat_id)
    formatted = [
        {"role": r, "message": m, "timestamp": ts}
        for r, m, ts in history
    ]
    return {"chat_id": chat_id, "history": formatted}

# --------------------------
# Delete chat history
# --------------------------
@app.delete("/api/history/{chat_id}")
def delete_chat_history(chat_id: str):
    chatbot.delete_history(chat_id)
    return {"status": "deleted", "chat_id": chat_id}

@app.get("/")
def home():
    return {"status": "backend running"}
