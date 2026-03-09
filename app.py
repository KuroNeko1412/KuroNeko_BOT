from flask import Flask, request
from linebot.v3.webhook import WebhookHandler
from linebot.v3.messaging import MessagingApi, ReplyMessageRequest, TextMessage
from linebot.v3.messaging import Configuration, ApiClient
from linebot.v3.webhooks import MessageEvent, TextMessageContent, MemberJoinedEvent, MemberLeftEvent
from linebot.v3.exceptions import InvalidSignatureError
from openai import OpenAI

import os
import time
import random

app = Flask(__name__)

CHANNEL_ACCESS_TOKEN = os.getenv("CHANNEL_ACCESS_TOKEN")
CHANNEL_SECRET = os.getenv("CHANNEL_SECRET")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

client = OpenAI(api_key=OPENAI_API_KEY)

users = {}
memory = {}
user_last_message = {}

SPAM_COOLDOWN = 3
ADMIN_IDS = ["PUT_ADMIN_USER_ID"]

def get_rank(msg):
    if msg >= 1000:
        return "Legend 🐉"
    elif msg >= 500:
        return "Elite ⚡"
    elif msg >= 200:
        return "Active 🔥"
    elif msg >= 50:
        return "Chatter 💬"
    else:
        return "Newbie 🌱"

def get_level(msg):
    return int(msg / 50) + 1

@app.route("/")
def home():
    return "KuroNeko Super AI BOT Running 😸"

@app.route("/callback", methods=['POST'])
def callback():

    signature = request.headers.get('X-Line-Signature','')
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        return "Invalid signature",400

    return "OK"

@handler.add(MemberJoinedEvent)
def welcome_user(event):

    with ApiClient(configuration) as api_client:

        line_bot_api = MessagingApi(api_client)

        user_id = event.joined.members[0].user_id
        profile = line_bot_api.get_profile(user_id)
        name = profile.display_name

        text = f"""
👋 ยินดีต้อนรับ {name}

ผมคือ KuroNeko AI BOT 😸
คุยกับผมได้เลย
พิมพ์ /help เพื่อดูคำสั่ง
"""

        line_bot_api.push_message(
            event.source.group_id,
            [TextMessage(text=text)]
        )

@handler.add(MemberLeftEvent)
def goodbye_user(event):

    with ApiClient(configuration) as api_client:

        line_bot_api = MessagingApi(api_client)

        text = "😢 มีสมาชิกออกจากกลุ่มไปแล้ว"

        line_bot_api.push_message(
            event.source.group_id,
            [TextMessage(text=text)]
        )

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):

    user_id = event.source.user_id
    user_message = event.message.text
    current_time = time.time()

    with ApiClient(configuration) as api_client:

        line_bot_api = MessagingApi(api_client)
        profile = line_bot_api.get_profile(user_id)
        name = profile.display_name

        if user_id in user_last_message:
            if current_time - user_last_message[user_id] < SPAM_COOLDOWN:

                reply = "พิมพ์เร็วเกินไปนะ 😅"

                line_bot_api.reply_message(
                    ReplyMessageRequest(
                        replyToken=event.reply_token,
                        messages=[TextMessage(text=reply)]
                    )
                )
                return

        user_last_message[user_id] = current_time

        if user_id not in users:
            users[user_id] = {"messages":0}

        users[user_id]["messages"] += 1

        msg_count = users[user_id]["messages"]
        rank = get_rank(msg_count)
        level = get_level(msg_count)

        if user_id not in memory:
            memory[user_id] = []

        memory[user_id].append({"role":"user","content":user_message})

        if len(memory[user_id]) > 10:
            memory[user_id] = memory[user_id][-10:]

        if user_message.lower() == "/help":

            reply = f"""
🤖 KuroNeko AI BOT

/help - คำสั่งทั้งหมด
/rank - ดูแรงค์
/level - ดูเลเวล
/stats - จำนวนข้อความ
/top - leaderboard
/game - เกมทายเลข
"""

        elif user_message.lower() == "/rank":

            reply = f"""
🏆 {name}

Rank: {rank}
Messages: {msg_count}
"""

        elif user_message.lower() == "/level":

            reply = f"""
⭐ {name}

Level: {level}
Messages: {msg_count}
"""

        elif user_message.lower() == "/stats":

            reply = f"{name} พิมพ์ไปแล้ว {msg_count} ข้อความ"

        elif user_message.lower() == "/top":

            sorted_users = sorted(users.items(), key=lambda x:x[1]["messages"], reverse=True)

            text = "🏆 Leaderboard\n\n"

            i = 1

            for u in sorted_users[:5]:

                text += f"{i}. {u[1]['messages']} messages\n"
                i += 1

            reply = text

        elif user_message.lower() == "/game":

            number = random.randint(1,10)
            users[user_id]["game"] = number

            reply = "🎮 เกมทายเลข 1-10 พิมพ์ตัวเลขมาทาย"

        elif user_message.isdigit():

            guess = int(user_message)

            if "game" in users[user_id]:

                if guess == users[user_id]["game"]:
                    reply = "🎉 ถูกต้อง!"
                else:
                    reply = "❌ ผิด ลองใหม่"

            else:
                reply = "พิมพ์ /game ก่อน"

        elif user_message.startswith("/say") and user_id in ADMIN_IDS:

            text = user_message.replace("/say","")

            reply = f"📢 ADMIN:{text}"

        else:

            ai = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role":"system","content":"คุณคือ KuroNeko แมว AI ที่คุยกับคนใน LINE อย่างเป็นมิตร"},
                    *memory[user_id]
                ]
            )

            reply = ai.choices[0].message.content

            memory[user_id].append({"role":"assistant","content":reply})

        line_bot_api.reply_message(
            ReplyMessageRequest(
                replyToken=event.reply_token,
                messages=[TextMessage(text=reply)]
            )
        )

if __name__ == "__main__":

    port = int(os.environ.get("PORT",5000))

    app.run(host="0.0.0.0", port=port)
