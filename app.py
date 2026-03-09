from flask import Flask, request
from linebot.v3.webhook import WebhookHandler
from linebot.v3.messaging import MessagingApi, ReplyMessageRequest, TextMessage
from linebot.v3.messaging import Configuration, ApiClient
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from linebot.v3.exceptions import InvalidSignatureError
import os
import random

app = Flask(_name_)

# หน้าเว็บหลัก
@app.route("/")
def home():
    return "KuroNeko BOT is running! 😸"

# อ่านค่าจาก Environment Variables
CHANNEL_ACCESS_TOKEN = os.getenv("CHANNEL_ACCESS_TOKEN")
CHANNEL_SECRET = os.getenv("CHANNEL_SECRET")

# ตั้งค่า LINE API
configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)

# สร้าง handler (สำคัญมาก)
handler = WebhookHandler(CHANNEL_SECRET)

# webhook จาก LINE
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers.get('X-Line-Signature', '')
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        return "Invalid signature", 400
    except Exception as e:
        print(e)
        return "Error", 200

    return "OK", 200

# คำตอบสุ่ม
responses = [
"ผมอยู่เป็นเพื่อนคุณได้นะ 😸",
"วันนี้เป็นยังไงบ้าง",
"อย่าลืมพักผ่อนด้วยนะ",
"ถ้าเหงาก็มาคุยกับผมได้เสมอ",
"คุณกำลังทำอะไรอยู่เหรอ",
"ผมดีใจที่ได้คุยกับคุณนะ",
"อย่าลืมดูแลตัวเองนะ",
"คุณทำให้วันนี้ของผมดีขึ้นเลย",
"ถ้าเหนื่อยก็พักบ้างนะ",
"ผมอยู่ตรงนี้เสมอเลย",
"มีอะไรอยากเล่าให้ผมฟังไหม",
"คุณยิ้มอยู่หรือเปล่า 😊",
"ผมชอบคุยกับคุณนะ",
"วันนี้อย่าลืมกินข้าวนะ 🍚",
"หวังว่าวันนี้จะเป็นวันที่ดีของคุณ",
"ผมเป็นห่วงคุณนะ",
"ขอบคุณที่มาคุยกับผม 😸",
"คุณสำคัญนะ อย่าลืมเลย",
"อย่าลืมดื่มน้ำด้วยนะ",
"พักผ่อนบ้างนะ"
]

# รับข้อความจากผู้ใช้
@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):

    user_message = event.message.text

    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)

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

        else:
            reply_text = random.choice(responses)

        line_bot_api.reply_message(
            ReplyMessageRequest(
                replyToken=event.reply_token,
                messages=[TextMessage(text=reply_text)]
            )
        )

# รันเซิร์ฟเวอร์
if _name_ == "_main_":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
