# # main.py
# import os
# from crew_runner import run_mdagents
# from google import generativeai as genai

# # Configure Gemini for general chat
# genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
# chat_model = genai.GenerativeModel("gemini-2.0-flash")


# def general_chatbot_reply(message: str) -> str:
#     """Plain general-purpose chatbot reply using Gemini."""
#     response = chat_model.generate_content(message)
#     text = getattr(response, "text", None) or "Sorry, I could not generate a reply."
#     return text.strip()


# def is_medical_query(text: str) -> bool:
#     """Same detector logic as api_server.py to keep behaviour consistent."""
#     medical_keywords = [
#         "pain", "fever", "infection", "disease", "treatment", "diagnose",
#         "doctor", "medical", "symptom", "injury", "surgery", "scan",
#         "ct", "mri", "ultrasound", "vomiting", "abdomen", "chest",
#         "breathing", "diabetes", "cancer", "year-old", "y/o",
#     ]
#     text = text.lower()
#     return any(word in text for word in medical_keywords)


# def chatbot_loop():
#     print("=== Smart MDAgents Medical + General Chat System ===")
#     print("Type 'exit' to quit.\n")

#     while True:
#         user_msg = input("You: ").strip()
#         if not user_msg:
#             continue

#         if user_msg.lower() == "exit":
#             print("Bot: Goodbye.")
#             break

#         # Medical queries → MDAgents pipeline
#         if is_medical_query(user_msg):
#             print("\n[Medical mode] Analyzing your case using MDAgents...\n")
#             result = run_mdagents(user_msg)
#             complexity = result.get("complexity", "UNKNOWN")
#             reasoning = result.get("reasoning", [])
#             final = result.get("final", "")

#             print(f"Complexity Level: {complexity}")
#             print("\nReasoning Summary:")
#             for i, r in enumerate(reasoning, start=1):
#                 print(f"  {i}. {r}")

#             print("\nFinal Integrated Opinion (Educational Only):")
#             print(final)
#             print(
#                 "\n[Disclaimer] This is NOT medical advice. "
#                 "Please consult a real doctor for diagnosis and treatment."
#             )
#             print()
#             continue

#         # Everything else → General chatbot
#         reply = general_chatbot_reply(user_msg)
#         print("Bot:", reply)
#         print()


# if __name__ == "__main__":
#     chatbot_loop()
# main.py
# import os
# import requests
# from crew_runner import run_mdagents


# # --------------------------------------
# # OpenRouter Settings (DeepSeek Model)
# # --------------------------------------
# OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
# OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# if not OPENROUTER_API_KEY:
#     raise ValueError("ERROR: OPENROUTER_API_KEY not found. Add it to your .env file.")


# def call_openrouter(prompt: str) -> str:
#     """
#     General chatbot reply using DeepSeek Chat (through OpenRouter).
#     Replaces Gemini completely.
#     """
#     payload = {
#         "model": "deepseek/deepseek-r1",
#         "messages": [
#             {"role": "system", "content": "You are a helpful, smart AI assistant."},
#             {"role": "user", "content": prompt}
#         ]
#     }

#     headers = {
#         "Authorization": f"Bearer {OPENROUTER_API_KEY}",
#         "Content-Type": "application/json",
#     }

#     response = requests.post(OPENROUTER_URL, json=payload, headers=headers)
#     data = response.json()

#     try:
#         return data["choices"][0]["message"]["content"].strip()
#     except Exception:
#         return f"[Error from OpenRouter] {data}"


# def is_medical_query(text: str) -> bool:
#     """Same detector logic as backend."""
#     medical_keywords = [
#         "pain", "fever", "infection", "disease", "treatment", "diagnose",
#         "doctor", "medical", "symptom", "injury", "surgery", "scan",
#         "ct", "mri", "ultrasound", "vomiting", "abdomen", "chest",
#         "breathing", "diabetes", "cancer", "year-old", "y/o",
#     ]
#     text = text.lower()
#     return any(word in text for word in medical_keywords)


# def chatbot_loop():
#     print("=== Smart MDAgents Medical + General Chat System ===")
#     print("Type 'exit' to quit.\n")

#     while True:
#         user_msg = input("You: ").strip()
#         if not user_msg:
#             continue

#         if user_msg.lower() == "exit":
#             print("Bot: Goodbye.")
#             break

#         # → MEDICAL QUERY: Use MDAgents
#         if is_medical_query(user_msg):
#             print("\n[Medical mode] Analyzing your case using MDAgents...\n")
#             result = run_mdagents(user_msg)

#             complexity = result.get("complexity", "UNKNOWN")
#             reasoning = result.get("reasoning", [])
#             final = result.get("final", "")

#             print(f"Complexity Level: {complexity}\n")
#             print("Reasoning Summary:")
#             for i, r in enumerate(reasoning, start=1):
#                 print(f"  {i}. {r}")

#             print("\nFinal Integrated Opinion (Educational Only):")
#             print(final)
#             print(
#                 "\n[Disclaimer] This is NOT medical advice. "
#                 "Please consult a real doctor for diagnosis and treatment."
#             )
#             print()
#             continue

#         # → NON-MEDICAL QUERY: Use OpenRouter (DeepSeek)
#         reply = call_openrouter(user_msg)
#         print("Bot:", reply)
#         print()


# if __name__ == "__main__":
#     chatbot_loop()
# main.py
# main.py
# main.py
import chatbot
from crew_runner import run_mdagents


def is_medical(text):
    keywords = ["pain", "fever", "diagnose", "treatment"]
    text = text.lower()
    return any(k in text for k in keywords)


def cli():
    chat_id = "cli_test"

    print("CLI Chat (type 'exit' to quit)\n")

    while True:
        msg = input("You: ").strip()

        if msg.lower() == "exit":
            break

        if is_medical(msg):
            chatbot.save_message(chat_id, "user", msg)
            result = run_mdagents(msg)
            reply = result.get("final", "No result")
            print("Bot:", reply)
            chatbot.save_message(chat_id, "assistant", reply)
        else:
            reply = chatbot.general_reply(chat_id, msg)
            print("Bot:", reply)


if __name__ == "__main__":
    cli()
