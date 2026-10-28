import os
import hmac
import hashlib
import base64
import requests
from flask import Flask, request, abort

app = Flask(__name__)

# ค่าลับ 2 ตัวนี้จะไปใส่ใน Render (ไม่เขียนลงโค้ด)
CHANNEL_SECRET = os.environ["LINE_CHANNEL_SECRET"]
CHANNEL_TOKEN = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]


def make_answer(text):
    """ตัดสินใจว่าจะตอบอะไร (ตอนนี้เป็นแบบง่าย ๆ ก่อน)"""
    text = text.strip()
    if "ราคา" in text:
        return "สินค้าของเราเริ่มต้นที่ 999 บาท สนใจรุ่นไหนพิมพ์ชื่อรุ่นมาได้เลยครับ"
    if "สั่ง" in text:
        return "สั่งซื้อได้เลยครับ กรุณาส่ง ชื่อ-ที่อยู่-สินค้าที่ต้องการ"
    return "สวัสดีครับ ต้องการสอบถามเรื่องอะไรครับ? พิมพ์ 'ราคา' หรือ 'สั่ง' ได้เลย"


def reply(reply_token, text):
    requests.post(
        "https://api.line.me/v2/bot/message/reply",
        headers={"Authorization": f"Bearer {CHANNEL_TOKEN}"},
        json={
            "replyToken": reply_token,
            "messages": [{"type": "text", "text": text}],
        },
        timeout=10,
    )


@app.route("/")
def home():
    return "Bot is running"


@app.route("/webhook", methods=["POST"])
def webhook():
    body = request.get_data()
    signature = request.headers.get("X-Line-Signature", "")

    # ตรวจว่าข้อความมาจาก LINE จริง ๆ
    digest = hmac.new(CHANNEL_SECRET.encode(), body, hashlib.sha256).digest()
    if not hmac.compare_digest(base64.b64encode(digest).decode(), signature):
        abort(400)

    for event in request.get_json().get("events", []):
        if event["type"] == "message" and event["message"]["type"] == "text":
            answer = make_answer(event["message"]["text"])
            reply(event["replyToken"], answer)

    return "OK"
