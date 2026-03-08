from flask import Flask, request, abort
from linebot.v3.webhook import WebhookHandler
from linebot.v3.messaging import MessagingApi, ReplyMessageRequest, TextMessage
from linebot.v3.messaging import Configuration, ApiClient
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from linebot.v3.exceptions import InvalidSignatureError
import os
import random

app = Flask(_name_)

@app.route("/")
def home():
    return "KuroNeko BOT is running! 😸"

CHANNEL_ACCESS_TOKEN = os.getenv("CHANNEL_ACCESS_TOKEN")
CHANNEL_SECRET = os.getenv("CHANNEL_SECRET")

configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers.get('X-Line-Signature')
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return "OK"


# ข้อความตอบสุ่มเวลาคุยเล่น
chat_responses = [
    "ผมอยู่เป็นเพื่อนคุณได้นะ 😸",
    "วันนี้เป็นยังไงบ้าง?",
    "อย่าลืมพักผ่อนด้วยนะ",
    "ถ้าเหงาก็มาคุยกับผมได้เสมอ",
    "ผมฟังอยู่นะ เล่าให้ฟังหน่อยสิ",
    "คุณเก่งมากเลยนะ 👍",
    "บางวันก็เหนื่อยได้ เป็นเรื่องปกติ",
    "ผมดีใจที่ได้คุยกับคุณ"
]

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):

    user_message = event.message.text.lower()

    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)

        # คำสั่งพื้นฐาน
        if user_message in ["สวัสดี", "hello", "hi"]:
            reply_text = "สวัสดีครับ 😸 ผมคือ KuroNeko BOT"

        elif user_message in ["เหงา", "เบื่อ"]:
            reply_text = "ถ้าเหงาก็มาคุยกับผมได้ ผมอยู่ตรงนี้นะ 😺"

        elif user_message in ["ทำอะไรอยู่"]:
            reply_text = "กำลังรอคุยกับคุณอยู่นะ"

        elif user_message in ["ฝันดี"]:
            reply_text = "ฝันดีนะครับ ขอให้หลับสบาย 😴"

        elif user_message in ["ขอบคุณ"]:
            reply_text = "ยินดีเสมอเลย 😸"

        # ถ้าไม่ตรงคำสั่ง ให้ตอบสุ่ม
        else:
            reply_text = random.choice(chat_responses)

        line_bot_api.reply_message(
            ReplyMessageRequest(
                replyToken=event.reply_token,
                messages=[TextMessage(text=reply_text)]
            )
        )


if _name_ == "_main_":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
