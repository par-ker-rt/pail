from flask import Flask, request, jsonify
from ollama_client import chat_with_bot

app = Flask(__name__)

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json()
    prompt = data.get("prompt", "")
    response = chat_with_bot(prompt)
    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(debug=True)
