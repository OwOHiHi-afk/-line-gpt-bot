import os
from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.messaging import MessagingApi, Configuration, ApiClient
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from openai import OpenAI

# 將這裡的金鑰換成你自己的
LINE_CHANNEL_ACCESS_TOKEN = "EWhpPck/LwnxLR7g1ZXpNTDPCwZwMp8PnlZB7K+sGaP9JAeab7cq936bpmkTYLQHJzWIiv6znbPNsNXeQEeKCqjerbRgg765sWZKg2OJdTmb9f9FOMSWBrTE8eQTKMuSb3mTtrkZ4zyyEunNAa/3AQdB04t89/1O/w1cDnyilFU="
LINE_CHANNEL_SECRET = "6b14d00ee2afeb1f5dba31c37a350c78"
OPENAI_API_KEY = "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"

app = Flask(__name__)

# 初始化 OpenAI Client
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# 初始化 LINE Messaging API
configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except Exception as e:
        print("❌ Webhook handler error:", e)
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    user_input = event.message.text

    try:
        # 建立與 GPT 的對話
        completion = openai_client.chat.completions.create(
            model="gpt-4o",  # 你可改成 gpt-3.5-turbo 或其他支援模型
            messages=[
                {"role": "system", "content": "你是一個友善的輔導員，協助使用者理解網路互動的風險。"},
                {"role": "user", "content": user_input}
            ]
        )

        reply_text = completion.choices[0].message.content.strip()

    except Exception as e:
        reply_text = f"發生錯誤：\n{e}"

    # 傳送回應
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message(
            reply_token=event.reply_token,
            messages=[{
                "type": "text",
                "text": reply_text
            }]
        )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
