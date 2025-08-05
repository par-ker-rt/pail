from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
import json
import os
from ollama_client import chat_with_bot

app = Flask(__name__)
CORS(app)

USERS_FILE = "users.json"

# ======= CONFIG ========= #
FREE_LIMIT = 30
PRO_PRICE = 5
GROUP_PRICE = 10
GRACE_DAYS = 7
# ======================== #

def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

def create_user_if_not_exist(username):
    users = load_users()
    if username not in users:
        users[username] = {
            "role": "Free",
            "message_count": 0,
            "last_reset": str(datetime.utcnow()),
            "upgraded_at": None
        }
        save_users(users)

def reset_message_count_if_new_day(user):
    last_reset = datetime.fromisoformat(user["last_reset"])
    now = datetime.utcnow()
    if now.date() > last_reset.date():
        user["message_count"] = 0
        user["last_reset"] = str(now)

def check_and_downgrade(user):
    if user["role"] in ["Pro", "Group"]:
        if not user["upgraded_at"]:
            return
        upgraded_date = datetime.fromisoformat(user["upgraded_at"])
        now = datetime.utcnow()
        if now > upgraded_date + timedelta(days=30 + GRACE_DAYS):
            user["role"] = "Free"
            user["upgraded_at"] = None

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username", "").strip()
    if not username:
        return jsonify({"error": "Thiếu tên người dùng"}), 400

    create_user_if_not_exist(username)
    users = load_users()
    user = users[username]

    reset_message_count_if_new_day(user)
    check_and_downgrade(user)
    save_users(users)

    return jsonify({"message": f"Chào {username}!", "role": user["role"], "count": user["message_count"]})

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    username = data.get("username", "").strip()
    prompt = data.get("prompt", "")

    if not username or not prompt:
        return jsonify({"error": "Thiếu tên người dùng hoặc nội dung"}), 400

    users = load_users()
    if username not in users:
        return jsonify({"error": "Người dùng chưa đăng nhập"}), 403

    user = users[username]
    reset_message_count_if_new_day(user)
    check_and_downgrade(user)

    # Check quota
    if user["role"] == "Free" and user["message_count"] >= FREE_LIMIT:
        return jsonify({"error": "Bạn đã hết 30 tin nhắn hôm nay. Nâng cấp để tiếp tục."}), 403

    # Gửi tới mô hình Ollama
    try:
        bot_reply = chat_with_bot(prompt)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    # Update message count
    if user["role"] != "Admin":
        user["message_count"] += 1

    users[username] = user
    save_users(users)

    return jsonify({"response": bot_reply})

@app.route("/upgrade", methods=["POST"])
def upgrade():
    data = request.get_json()
    username = data.get("username", "").strip()
    tier = data.get("tier", "")  # "Pro" hoặc "Group"

    if tier not in ["Pro", "Group"]:
        return jsonify({"error": "Sai loại thẻ"}), 400

    users = load_users()
    if username not in users:
        return jsonify({"error": "Không tìm thấy người dùng"}), 404

    users[username]["role"] = tier
    users[username]["upgraded_at"] = str(datetime.utcnow())
    save_users(users)

    return jsonify({"message": f"Đã nâng cấp {username} lên {tier}."})

if __name__ == "__main__":
    app.run(debug=True)
