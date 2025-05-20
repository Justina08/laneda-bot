# app.py
"""
LanedaBot – minimal Flask + Gupshup WhatsApp bot
Handles GET/HEAD for v2 webhook validation, and POST for real messages.
"""

import os, json, logging, requests
from flask import Flask, request, jsonify

# ───── Configuration ─────────────────────────────────────────────────
# (move secrets into Railway → Variables in the UI)
GUPSHUP_API_URL = "https://api.gupshup.io/sm/api/v1/msg"
APP_TOKEN       = os.environ["GUPSHUP_API_KEY"]
SOURCE_PHONE    = os.environ["GUPSHUP_SOURCE"]

# ───── Flask setup ────────────────────────────────────────────────────
app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

# ───── Health‐check (public root) ────────────────────────────────────
@app.route("/", methods=["GET", "HEAD"])
def home():
    return "✅ LanedaBot is live on Railway!", 200

# ───── Webhook endpoint ───────────────────────────────────────────────
@app.route("/webhook", methods=["GET", "HEAD", "POST"])
def webhook():
    # 1) HEAD/GET probe for v2 format → just return 200
    if request.method in ("GET", "HEAD"):
        return jsonify({"status": "ok"}), 200

    # 2) Real messages arrive as POST with JSON
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"status": "error", "msg": "no json"}), 400

    # Extract & reply
    try:
        sender  = data["payload"]["sender"]["phone"]
        text_in = data["payload"]["payload"]["text"]
    except KeyError:
        return jsonify({"status": "error", "msg": "malformed payload"}), 400

    # Decide and send
    reply = decide_reply(text_in)
    ok    = send_message(sender, reply)
    if not ok:
        logging.error("Failed to send to %s", sender)

    return jsonify({"status": "ok"}), 200

# ───── Bot logic ──────────────────────────────────────────────────────
def decide_reply(text: str) -> str:
    t = text.strip().lower()
    if t in ("hi", "hello"):
        return "👋 Hello! Reply 1 for services."
    if t == "1":
        return "We offer AI lead generation & WhatsApp automation."
    return "❓ Send ‘hi’ or ‘1’."

# ───── Gupshup API call ───────────────────────────────────────────────
def send_message(destination: str, text: str) -> bool:
    headers = {
        "apikey": APP_TOKEN,
        "Content-Type": "application/x-www-form-urlencoded",
    }
    body = {
        "channel":     "whatsapp",
        "source":      SOURCE_PHONE,
        "destination": destination,
        "message":     json.dumps({"type": "text", "text": text}),
    }
    r = requests.post(GUPSHUP_API_URL, headers=headers, data=body, timeout=10)
    logging.info("Gupshup API %s %s", r.status_code, r.text)
    return r.ok

# ───── Entrypoint ─────────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
