from flask import Flask, request, abort
from linebot.v3.webhook import WebhookHandler
from linebot.v3.messaging import MessagingApi, ReplyMessageRequest, TextMessage
from linebot.v3.messaging import Configuration, ApiClient
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from linebot.v3.exceptions import InvalidSignatureError
import os
import random

app = Flask(__name__)

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

responses = [
    "ผมอยู่เป็นเพื่อนคุณได้นะ 😸",
    "วันนี้เป็นยังไงบ้าง",
    "อย่าลืมพักผ่อนด้วยนะ",
    "ถ้าเหงาก็มาคุยกับผมได้เสมอ",
]

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
            reply_text = random.choice([
                "ผมอยู่เป็นเพื่อนคุณได้นะ 😸",
                "วันนี้เป็นยังไงบ้าง",
                "อย่าลืมพักผ่อนด้วยนะ",
                "ถ้าเหงาก็มาคุยกับผมได้เสมอ"
            ])

        line_bot_api.reply_message(
            ReplyMessageRequest(
                replyToken=event.reply_token,
                messages=[TextMessage(text=reply_text)]
            )
        )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
