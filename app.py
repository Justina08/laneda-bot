# app.py
"""
LanedaBot – minimal Flask + Gupshup WhatsApp bot
• Receives messages at /webhook
• Sends replies back via Gupshup’s Send-Message API
Deploy tested on Railway (May 2025)
"""
from flask import Flask, request, jsonify
import os, requests, json, logging

# ---------------------------------------------------------------------
# 1️⃣  Configuration – keep secrets OUT of your code!
# ---------------------------------------------------------------------
GUPSHUP_API_URL = "https://api.gupshup.io/sm/api/v1/msg"
APP_TOKEN       = "vmtlnilqraxkzfapylijqftvb1odasdj"
SOURCE_PHONE    = "447495867459"          # your approved WhatsApp number

# ---------------------------------------------------------------------
# 2️⃣  Flask setup
# ---------------------------------------------------------------------
from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# Health-check on /
@app.route("/", methods=["GET"])
def home():
    return "✅ LanedaBot is live on Railway!", 200

# The real webhook on /webhook
@app.route("/webhook", methods=["GET", "HEAD", "POST"])
def webhook():
    # 1) Gupshup validator uses GET/HEAD
    if request.method in ("GET", "HEAD"):
        return jsonify({"status": "ok"}), 200

    # 2) Real WhatsApp messages come POST → JSON
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"status": "error", "msg": "no json"}), 400

    # … your existing parse/send logic …
    sender  = data["payload"]["sender"]["phone"]
    text_in = data["payload"]["payload"]["text"]
    text_out = decide_reply(text_in)
    send_message(sender, text_out)

    return jsonify({"status": "ok"}), 200
# -------------------------------------------------------------
# 0)  Configuration
# -------------------------------------------------------------
VERIFY_TOKEN = os.getenv("GS_VERIFY_TOKEN", "lanedabot-secret")  # choose any string

# -------------------------------------------------------------
# 1)  Webhook route  (one definition only!)
# -------------------------------------------------------------
@app.route("/webhook", methods=["GET", "HEAD", "POST"])
def webhook():
    # A. Meta / Gupshup validator probe ------------------------
    if request.method in ("GET", "HEAD"):
        mode      = request.args.get("hub.mode")
        challenge = request.args.get("hub.challenge")
        token     = request.args.get("hub.verify_token")

        # If it's the Meta-style handshake, echo the challenge
        if mode == "subscribe" and token == VERIFY_TOKEN:
            # must return the *raw* challenge, not JSON
            return challenge, 200, {"Content-Type": "text/plain"}

        # Otherwise it's just a HEAD probe → say OK
        return "ok", 200

    # B. Real WhatsApp messages arrive as POST -----------------
    payload = request.get_json(silent=True)
    if payload is None:
        return jsonify({"status": "error", "msg": "no json"}), 400

    # --- your existing logic ---------------------------------
    sender  = payload["payload"]["sender"]["phone"]
    text_in = payload["payload"]["payload"]["text"]

    # decide_reply() & send_message() are the helpers you already wrote
    text_out = decide_reply(text_in)
    send_message(sender, text_out)

    return jsonify({"status": "ok"}), 200

    payload = request.get_json(force=True)       # force=True → 400 if no JSON
    logging.info("Webhook payload: %s", json.dumps(payload, indent=2))

    try:
        text_in   = payload["payload"]["payload"]["text"]
        sender_id = payload["payload"]["sender"]["phone"]
    except KeyError as err:
        logging.exception("Malformed payload – missing %s", err)
        return jsonify({"status": "error", "msg": "bad payload"}), 400

    # ---------------- Bot logic (tiny demo) ----------------
    text_out = decide_reply(text_in)

    # ---------------- Send the reply -----------------------
    ok = send_message(sender_id, text_out)
    if not ok:
        # Even if Gupshup fails we still ACK, otherwise it will retry
        logging.error("Failed to send reply to %s", sender_id)

    return jsonify({"status": "ok"}), 200


# ---------------------------------------------------------------------
# 3️⃣  Your bot’s “brain” – expand as you wish
# ---------------------------------------------------------------------
def decide_reply(text: str) -> str:
    """Return a text reply based on the incoming message."""
    t = text.strip().lower()

    if t in {"hi", "hello"}:
        return (
            "👋 Hi there! Welcome to *Laneda SmartTech*.\n"
            "Reply 1️⃣ to learn about our services."
        )
    if t == "1":
        return (
            "🌟 We offer AI-powered lead generation and WhatsApp automation.\n"
            "Reply 2️⃣ for a live demo or 3️⃣ for pricing."
        )
    if t == "2":
        return "📅 Great! Our team will contact you to schedule a demo."
    if t == "3":
        return "💰 Our starter plan is £49/month. Reply 4️⃣ to talk to sales."
    return "❓ Sorry, I didn’t understand that. Please reply with 1 to begin."


# ---------------------------------------------------------------------
# 4️⃣  Helper – call Gupshup Send-Message API
# ---------------------------------------------------------------------
def send_message(destination: str, text: str) -> bool:
    """
    destination : user's phone (string)
    text        : message to send
    Returns True on 200 OK else False.
    """
    headers = {
        "apikey": APP_TOKEN,
        "Content-Type": "application/x-www-form-urlencoded",
    }
    body = {
        "channel":      "whatsapp",
        "source":       SOURCE_PHONE,
        "destination":  destination,
        "message":      json.dumps({"type": "text", "text": text}),
        "src.name":     "LanedaBot",
    }

    resp = requests.post(GUPSHUP_API_URL, headers=headers, data=body, timeout=10)
    logging.info("Gupshup API %s – %s", resp.status_code, resp.text)
    return resp.ok


# ---------------------------------------------------------------------
# 5️⃣  Entry-point – Railway runs `python app.py`
# ---------------------------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))    # Railway injects $PORT
    app.run(host="0.0.0.0", port=port)
