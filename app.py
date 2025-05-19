from flask import Flask, request
import requests
import json

app = Flask(__name__)

# 🔐 Replace these with YOUR details from Gupshup dashboard
GUPSHUP_API_URL = "GUPSHUP_API_URL = "https://api.gupshup.io/sm/api/v1/msg"
APP_TOKEN = "GUPSHUP_API_URL = "https://api.gupshup.io/sm/api/v1/msg"
SOURCE_PHONE = "447495867459"  # Your approved WhatsApp number

@app.route("/", methods=["GET"])
def home():
    return "✅ LanedaBot is Live on Railway!"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    try:
        message = data['payload']['payload']['text']
        sender = data['payload']['sender']['phone']
        print("From:", sender, "| Message:", message)

        # Basic logic
        if "hi" in message.lower():
            send_message(sender, "👋 Hi there! Welcome to Laneda SmartTech.\nReply 1️⃣ to learn about our services.")
        elif message.strip() == "1":
            send_message(sender, "🌟 We offer AI-powered lead generation and WhatsApp automation.\nWould you like a demo or pricing?")
        else:
            send_message(sender, "❓ Sorry, I didn’t understand that. Please reply with 1 to begin.")
    except Exception as e:
        print("❌ Error:", e)
    return "ok", 200

def send_message(to, msg):
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "apikey": APP_TOKEN
    }
    payload = {
        "channel": "whatsapp",
        "source": SOURCE_PHONE,
        "destination": to,
        "message": json.dumps({"type": "text", "text": msg}),
        "src.name": "LanedaBot"
    }
    requests.post(GUPSHUP_API_URL, headers=headers, data=payload)

if __name__ == "__main__":
    app.run()

