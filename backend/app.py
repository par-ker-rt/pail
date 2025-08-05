from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)

USERS_FILE = 'backend/users.json'
DAILY_LIMIT = 40

def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, 'r') as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_id = data.get('user_id')
    message = data.get('message')

    if not user_id or not message:
        return jsonify({'error': 'Missing user_id or message'}), 400

    users = load_users()
    user = users.get(user_id, {"tier": "free", "messages_today": 0})

    if user["tier"] in ["admin", "pro"]:
        pass
    elif user["messages_today"] >= DAILY_LIMIT:
        return jsonify({'error': 'Daily limit reached'}), 403
    else:
        user["messages_today"] += 1

    # Tạm thời phản hồi lại chính message
    reply = f"You said: {message}"

    users[user_id] = user
    save_users(users)

    return jsonify({'reply': reply})

@app.route('/reset', methods=['POST'])
def reset():
    users = load_users()
    for user in users.values():
        user["messages_today"] = 0
    save_users(users)
    return jsonify({'message': 'Reset successful'})

if __name__ == '__main__':
    app.run(debug=True)
app = Flask(__name__)
