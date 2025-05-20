# app.py
"""
LanedaBot – minimal Flask + Gupshup WhatsApp bot
• GET/HEAD on / → health-check
• GET/HEAD/POST on /webhook → v2 validation + incoming messages
"""

import os
import json
import logging
import requests
from flask import Flask, request, jsonify

# ───── 0) Logging & Env-Vars Debug ────────────────────────────────
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

# Log the values Railway injects so we can confirm they exist
logging.info("ENV • GUPSHUP_API_KEY=%s", os.getenv("GUPSHUP_API_KEY"))
logging.info("ENV • GUPSHUP_SOURCE=%s", os.getenv("GUPSHUP_SOURCE"))
logging.info("ENV • PORT=%s", os.getenv("PORT"))

# ───── 1) Configuration (from env-vars) ───────────────────────────
GUPSHUP_API_URL = "https://api.gupshup.io/sm/api/v1/msg"
APP_TOKEN       = os.environ["GUPSHUP_API_KEY"]     # must match Railway Variables key
SOURCE_PHONE    = os.environ["GUPSHUP_SOURCE"]      # must match Railway Variables key

# ───── 2) Flask setup ─────────────────────────────────────────────
app = Flask(__name__)

# ───── 3) Health-check endpoint ───────────────────────────────────
@app.route("/", methods=["GET", "HEAD"])
def home():
    return "✅ LanedaBot is live on Railway!", 200

# ───── 4) Webhook endpoint ────────────────────────────────────────
@app.route("/webhook", methods=["GET", "HEAD", "POST"])
def webhook():
    # A) Validator (GET or HEAD) for v2 format → HTTP 200
    if request.method in ("GET", "HEAD"):
        return jsonify({"status": "ok"}), 200

    # B) Real messages come in as POST with JSON body
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"status": "error", "msg": "no json"}), 400

    # Extract phone & text, handle malformed payloads
    try:
        sender  = data["payload"]["sender"]["phone"]
        text_in = data["payload"]["payload"]["text"]
    except (TypeError, KeyError):
        return jsonify({"status": "error", "msg": "malformed payload"}), 400

    # Decide and send reply
    reply = decide_reply(text_in)
    success = send_message(sender, reply)
    if not success:
        logging.error("Failed to send message to %s", sender)

    return jsonify({"status": "ok"}), 200

# ───── 5) Bot-logic helper ─────────────────────────────────────────
def decide_reply(text: str) -> str:
    t = text.strip().lower()
    if t in ("hi", "hello"):
        return "👋 Hello! Reply 1 for services."
    if t == "1":
        return "We offer AI lead generation & WhatsApp automation."
    return "❓ Send ‘hi’ or ‘1’."

# ───── 6) Gupshup send helper ─────────────────────────────────────
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
    resp = requests.post(GUPSHUP_API_URL, headers=headers, data=body, timeout=10)
    logging.info("Gupshup API %s – %s", resp.status_code, resp.text)
    return resp.ok

# ───── 7) Entry-point for Railway ───────────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
