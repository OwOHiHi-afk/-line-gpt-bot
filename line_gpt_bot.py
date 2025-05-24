from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import openai
import os

app = Flask(__name__)

# 環境變數設定（從 Render 的 Environment Variables 讀進來）
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)
openai.api_key = OPENAI_API_KEY

@app.route("/", methods=["GET"])
def home():
    return "LINE GPT Bot is running!"

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return "OK"

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_input = event.message.text

    # 自動判斷是否觸發模擬情境
    if "模擬" in user_input:
        system_prompt = """你現在是一位法律教育講師，幫助使用者識別網路互動中的法律風險。
請產出三個情境類似（但不同）的選項（3～4個附emoji）
每個選項的風險請說明清楚，不要用問句。
"""
    else:
        system_prompt = "請使用教育性語氣回應以下內容："

    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]
    )

    reply_text = response.choices[0].message.content
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
