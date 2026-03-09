from flask import Flask, request, abort
import random
import time

from linebot.v3 import WebhookHandler
from linebot.v3.messaging import *
from linebot.v3.webhooks import *

CHANNEL_ACCESS_TOKEN = "YOUR_CHANNEL_ACCESS_TOKEN"
CHANNEL_SECRET = "YOUR_CHANNEL_SECRET"

configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

app = Flask(__name__)

# =========================
# DATABASE (MEMORY)
# =========================

owners = []
admins = []

bot_enabled = True

user_exp = {}
user_messages = {}

spam_tracker = {}

poll_data = None
poll_votes = {}

# =========================
# AI RESPONSES
# =========================

ai_responses = [
"วันนี้เป็นยังไงบ้าง",
"เหนื่อยไหมวันนี้",
"กินข้าวหรือยัง",
"ผมอยู่คุยเป็นเพื่อนนะ",
"อย่าลืมพักผ่อนด้วย",
"กำลังทำอะไรอยู่",
"ผมเหงาเหมือนกัน",
"เล่าอะไรให้ฟังหน่อยสิ",
"วันนี้มีอะไรสนุกไหม",
"ขอบคุณที่คุยกับผมนะ"
]

# =========================
# HELPER FUNCTIONS
# =========================

def is_admin(uid):
    return uid in owners or uid in admins

def get_level(exp):
    return int(exp ** 0.5)

# =========================
# WEBHOOK
# =========================

@app.route("/callback", methods=['POST'])
def callback():

    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except:
        abort(400)

    return 'OK'

# =========================
# MESSAGE EVENT
# =========================

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):

    global poll_data, poll_votes, bot_enabled

    text = event.message.text
    user_id = event.source.user_id

    with ApiClient(configuration) as api_client:

        line_bot_api = MessagingApi(api_client)

        profile = line_bot_api.get_profile(user_id)
        name = profile.display_name

        # BOT OFF CHECK
        if not bot_enabled and not is_admin(user_id):
            return

        # =================
        # ANTISPAM
        # =================

        now = time.time()

        if user_id not in spam_tracker:
            spam_tracker[user_id] = []

        spam_tracker[user_id].append(now)

        spam_tracker[user_id] = [
            t for t in spam_tracker[user_id]
            if now - t < 5
        ]

        if len(spam_tracker[user_id]) > 5:

            reply = f"{name} พิมพ์เร็วเกินไป 😅"

            line_bot_api.reply_message(
                ReplyMessageRequest(
                    replyToken=event.reply_token,
                    messages=[TextMessage(text=reply)]
                )
            )
            return

        # =================
        # LEVEL SYSTEM
        # =================

        user_messages[user_id] = user_messages.get(user_id,0)+1
        user_exp[user_id] = user_exp.get(user_id,0)+5

        # =================
        # COMMANDS
        # =================

        # REGISTER OWNER
        if text == "/register":

            if len(owners) == 0:
                owners.append(user_id)
                reply = f"👑 {name} เป็น Owner แล้ว"
            else:
                reply = "Owner ถูกตั้งแล้ว"

        # ADD ADMIN
        elif text.startswith("/addadmin"):

            if not is_admin(user_id):
                reply = "❌ เฉพาะแอดมิน"

            else:

                mention = event.message.mention

                if mention:

                    target = mention.mentionees[0].user_id

                    if target not in admins:

                        admins.append(target)

                        profile = line_bot_api.get_profile(target)

                        reply = f"✅ เพิ่ม {profile.display_name} เป็นแอดมิน"

                    else:

                        reply = "เป็นแอดมินอยู่แล้ว"

                else:

                    reply = "กรุณา @mention คน"

        # REMOVE ADMIN
        elif text.startswith("/removeadmin"):

            if not is_admin(user_id):

                reply = "❌ เฉพาะแอดมิน"

            else:

                mention = event.message.mention

                if mention:

                    target = mention.mentionees[0].user_id

                    if target in admins:

                        admins.remove(target)

                        profile = line_bot_api.get_profile(target)

                        reply = f"🗑 ลบ {profile.display_name}"

                    else:

                        reply = "ไม่ใช่แอดมิน"

        # BOT OFF
        elif text == "/bot off":

            if not is_admin(user_id):

                reply = "❌ เฉพาะแอดมิน"

            else:

                bot_enabled = False
                reply = f"🔴 {name} ปิดบอทแล้ว"

        # BOT ON
        elif text == "/bot on":

            if not is_admin(user_id):

                reply = "❌ เฉพาะแอดมิน"

            else:

                bot_enabled = True
                reply = f"🟢 {name} เปิดบอทแล้ว"

        # ANNOUNCE
        elif text.startswith("/announce"):

            if not is_admin(user_id):

                reply = "❌ เฉพาะแอดมิน"

            else:

                msg = text.replace("/announce ","")

                reply = f"📢 ประกาศจาก {name}\n\n{msg}"

        # LEVEL
        elif text == "/level":

            exp = user_exp.get(user_id,0)
            level = get_level(exp)
            count = user_messages.get(user_id,0)

            reply = f"""
🏆 {name}

Level : {level}
EXP : {exp}
Messages : {count}
"""

        # LEADERBOARD
        elif text == "/top":

            ranking = sorted(
                user_messages.items(),
                key=lambda x: x[1],
                reverse=True
            )

            msg = "🏆 Leaderboard\n\n"

            for i,(uid,count) in enumerate(ranking[:10]):

                p = line_bot_api.get_profile(uid)

                msg += f"{i+1}. {p.display_name} - {count}\n"

            reply = msg

        # CREATE POLL
        elif text.startswith("/poll"):

            options = text.replace("/poll ","").split(",")

            poll_data = options
            poll_votes = {}

            buttons = []

            for i,opt in enumerate(options):

                buttons.append({
                    "type":"button",
                    "action":{
                        "type":"message",
                        "label":opt,
                        "text":f"/vote {i+1}"
                    }
                })

            flex = {
              "type":"flex",
              "altText":"Poll",
              "contents":{
                "type":"bubble",
                "body":{
                  "type":"box",
                  "layout":"vertical",
                  "contents"
                    {"type":"text","text":"📊 โพลใหม่","weight":"bold"}
                  ]
                },
                "footer":{
                  "type":"box",
                  "layout":"vertical",
                  "contents":buttons
                }
              }
            }

            line_bot_api.reply_message(
                ReplyMessageRequest(
                    replyToken=event.reply_token,
                    messages=[flex]
                )
            )
            return

        # VOTE
        elif text.startswith("/vote"):

            vote = int(text.split(" ")[1])

            if user_id in poll_votes:

                reply = "❌ คุณโหวตแล้ว"

            else:

                poll_votes[user_id] = vote

                reply = f"{name} โหวต {poll_data[vote-1]}"

        # RESULT
        elif text == "/result":

            result = {}

            for v in poll_votes.values():
                result[v] = result.get(v,0)+1

            msg = "📊 ผลโหวต\n\n"

            total = max(1,len(poll_votes))

            for i,opt in enumerate(poll_data):

                count = result.get(i+1,0)

                percent = int((count/total)*100)

                bar = "█"*(percent//10)

                msg += f"{opt}\n{bar} {percent}% ({count})\n\n"

            reply = msg

        # HELP
        elif text == "/help":

            reply = """
🤖 คำสั่งบอท

/register
/addadmin @คน
/removeadmin @คน

/bot on
/bot off

/announce

/level
/top

/poll
/vote
/result

/help
"""

        # AI CHAT
        else:

            reply = f"{name} {random.choice(ai_responses)}"

        line_bot_api.reply_message(
            ReplyMessageRequest(
                replyToken=event.reply_token,
                messages=[TextMessage(text=reply)]
            )
        )

# =========================
# MEMBER JOIN
# =========================

@handler.add(MemberJoinedEvent)
def welcome(event):

    with ApiClient(configuration) as api_client:

        line_bot_api = MessagingApi(api_client)

        user_id = event.joined.members[0].user_id

        profile = line_bot_api.get_profile(user_id)

        name = profile.display_name

        line_bot_api.push_message(
            event.source.group_id,
            [TextMessage(text=f"👋 ยินดีต้อนรับ {name}")]
        )

# =========================
# MEMBER LEFT
# =========================

@handler.add(MemberLeftEvent)
def goodbye(event):

    with ApiClient(configuration) as api_client:

        line_bot_api = MessagingApi(api_client)

        line_bot_api.push_message(
            event.source.group_id,
            [TextMessage(text="😢 มีสมาชิกออกจากกลุ่ม")]
        )

if __name__ == "__main__":
    app.run(port=3000)
