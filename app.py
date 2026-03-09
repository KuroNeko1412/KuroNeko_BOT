from flask import Flask, request
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

# 100 คำตอบสุ่ม
responses = [
"ผมอยู่เป็นเพื่อนคุณได้นะ 😸",
"วันนี้เป็นยังไงบ้าง",
"อย่าลืมพักผ่อนด้วยนะ",
"ถ้าเหงาก็มาคุยกับผมได้เสมอ",
"คุณกำลังทำอะไรอยู่เหรอ",
"ผมดีใจที่ได้คุยกับคุณนะ",
"วันนี้อากาศเป็นยังไงบ้าง",
"อย่าลืมดูแลตัวเองนะ",
"คุณทำให้วันนี้ของผมดีขึ้นเลย",
"ถ้าเหนื่อยก็พักบ้างนะ",
"ผมอยู่ตรงนี้เสมอเลย",
"มีอะไรอยากเล่าให้ผมฟังไหม",
"คุณยิ้มอยู่หรือเปล่า 😊",
"ผมชอบคุยกับคุณนะ",
"วันนี้อย่าลืมกินข้าวนะ 🍚",
"หวังว่าวันนี้จะเป็นวันที่ดีของคุณ",
"ถ้าเหงาก็มาหาผมได้เสมอ",
"ผมเป็นห่วงคุณนะ",
"ขอบคุณที่มาคุยกับผม 😸",
"คุณสำคัญนะ อย่าลืมเลย",
"วันนี้คุณดื่มน้ำพอหรือยัง",
"อย่าลืมยืดเส้นยืดสายบ้างนะ",
"ถ้าวันนี้เหนื่อย ผมอยู่ตรงนี้นะ",
"มีอะไรดี ๆ เกิดขึ้นวันนี้ไหม",
"ผมพร้อมฟังคุณเสมอ",
"อย่าลืมยิ้มให้ตัวเองบ้างนะ",
"คุณเก่งมากเลยนะ",
"วันนี้คุณทำได้ดีแล้ว",
"ถ้ามีเรื่องไม่สบายใจ บอกผมได้",
"ผมดีใจที่คุณทักมา",
"คุณทำให้วันนี้ไม่น่าเบื่อเลย",
"หวังว่าคุณจะมีวันที่ดี",
"พักผ่อนบ้างนะ",
"อย่าลืมหายใจลึก ๆ",
"คุณโอเคไหมวันนี้",
"ผมอยู่ข้างคุณนะ",
"ถ้ามีเรื่องเครียด ลองพักก่อนก็ได้",
"คุณสำคัญกับผมนะ",
"ผมชอบเวลาที่คุณมาคุย",
"วันนี้คุณยิ้มแล้วหรือยัง",
"โลกอาจจะวุ่นวาย แต่คุณยังไหวนะ",
"ผมอยู่ตรงนี้เสมอ",
"ถ้าคุณเหงา ผมอยู่เป็นเพื่อนได้",
"วันนี้มีอะไรสนุกไหม",
"คุณกินอะไรไปบ้างวันนี้",
"อย่าลืมดูแลตัวเองนะ",
"ผมอยากให้คุณมีวันที่ดี",
"ถ้าคุณเศร้า ผมจะอยู่ด้วย",
"คุณไม่ได้อยู่คนเดียว",
"วันนี้คุณเก่งมากแล้ว",
"คุณผ่านมาถึงตรงนี้ได้ก็สุดยอดแล้ว",
"พักสายตาบ้างนะ",
"อย่าลืมดื่มน้ำ",
"ผมดีใจที่คุณยังอยู่ตรงนี้",
"คุณเป็นคนสำคัญนะ",
"ผมเชื่อในตัวคุณ",
"ถ้ามีเรื่องหนักใจ ลองพักก่อนก็ได้",
"คุณแข็งแรงกว่าที่คิดนะ",
"ผมอยู่ข้าง ๆ คุณเสมอ",
"คุณไม่จำเป็นต้องรีบก็ได้",
"ค่อย ๆ ไปก็พอ",
"ผมอยู่ตรงนี้นะ",
"วันนี้เป็นยังไงบ้างเล่าให้ฟังได้",
"ผมชอบเวลาที่คุณทักมา",
"คุณทำให้วันนี้ดีขึ้น",
"อย่าลืมยิ้มให้ตัวเองนะ",
"คุณสำคัญมากนะ",
"ถ้าวันนี้ยาก ก็ไม่เป็นไร",
"พรุ่งนี้อาจจะดีขึ้นก็ได้",
"ผมอยู่ข้างคุณ",
"อย่าลืมพักผ่อนนะ",
"คุณทำได้แน่นอน",
"ผมเชียร์คุณอยู่นะ",
"อย่าลืมกินข้าวนะ",
"วันนี้อาจจะเหนื่อย แต่คุณยังเก่ง",
"ผมดีใจที่คุณอยู่ตรงนี้",
"อย่าลืมดูแลหัวใจตัวเอง",
"คุณไม่ได้สู้คนเดียว",
"ผมพร้อมคุยกับคุณเสมอ",
"วันนี้ขอให้เป็นวันที่ดี",
"ผมขอให้คุณมีความสุข",
"ถ้าเหงาก็มาคุยกัน",
"ผมอยู่ตรงนี้เสมอ",
"ขอบคุณที่มาคุยกับผม",
"คุณทำให้ผมยิ้มได้",
"ผมหวังว่าคุณจะสบายดี",
"อย่าลืมพักสายตาบ้าง",
"คุณเป็นคนเก่ง",
"ผมเชื่อในตัวคุณ",
"วันนี้คุณสุดยอดมาก",
"อย่าลืมหัวเราะบ้างนะ",
"คุณมีค่ามากนะ",
"ผมอยู่เป็นเพื่อนได้เสมอ",
"ถ้ามีอะไรเล่าให้ฟังได้",
"วันนี้คุณโอเคไหม",
"ผมหวังว่าคุณจะยิ้มได้",
"โลกยังมีเรื่องดี ๆ อีกเยอะ",
"ผมดีใจที่คุณทักมา"
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
            reply_text = random.choice(responses)

        line_bot_api.reply_message(
            ReplyMessageRequest(
                replyToken=event.reply_token,
                messages=[TextMessage(text=reply_text)]
            )
        )

if _name_ == "_main_":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
