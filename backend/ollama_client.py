import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3"  # Đổi thành tên model bạn đang dùng nếu khác

def chat_with_bot(prompt, chat_history=None):
    if chat_history is None:
        chat_history = []

    messages = [{"role": "user", "content": prompt}]
    for msg in chat_history:
        messages.append(msg)

    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False
    }

    response = requests.post(OLLAMA_URL, json=payload)
    response.raise_for_status()
    return response.json()["response"]
