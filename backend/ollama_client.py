import requests
import os

# Đọc URL và model từ biến môi trường (nếu không có thì dùng mặc định)
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3")

def chat_with_bot(prompt, chat_history=None):
    if chat_history is None:
        chat_history = []

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload)
        response.raise_for_status()
        return response.json()["response"]
    except Exception as e:
        return f"Lỗi khi gọi model: {e}"
