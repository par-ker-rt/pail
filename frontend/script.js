async function sendMessage() {
    const input = document.getElementById("user-input");
    const message = input.value.trim();
    if (!message) return;

    appendMessage("🧑 You", message);

    input.value = "";
    
    const response = await fetch("http://localhost:5000/chat", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            user_id: "user1",
            message: message
        })
    });

    const data = await response.json();
    if (data.reply) {
        appendMessage("🤖 Pail", data.reply);
    } else if (data.error) {
        appendMessage("⚠️ Error", data.error);
    }
}

function appendMessage(sender, text) {
    const chatBox = document.getElementById("chat-box");
    const msg = document.createElement("div");
    msg.textContent = `${sender}: ${text}`;
    chatBox.appendChild(msg);
    chatBox.scrollTop = chatBox.scrollHeight;
}
