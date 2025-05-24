from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import openai
import os

app = Flask(__name__)

# 👉 把這裡換成你自己的金鑰
LINE_CHANNEL_ACCESS_TOKEN = "你的 Access Token"
LINE_CHANNEL_SECRET = "你的 Secret"
OPENAI_API_KEY = "你的 OpenAI API Key"

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)
openai.api_key = OPENAI_API_KEY

@app.route("/")
def home():
    return "LINE + GPT 模擬器已啟動"

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_input = event.message.text

    # 自動判斷是否觸發模擬情境
    if "模擬" in user_input:
        system_prompt = (
            "你是一位法律教育導師，幫助使用者識別網路互動中的法律風險。"
            "請產生：1. 情境描述（2段）2. 選項（3～4個，附emoji）3. 每個選項的風險說明。"
            "語氣要中立親切，不要開場白。"
        )
    else:
        system_prompt = "請使用教育性語氣回應以下內容："

    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]
    )

    reply = response.choices[0].message.content
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply)
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
