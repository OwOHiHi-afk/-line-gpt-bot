from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import openai

app = Flask(__name__)

# 套入你的金鑰
LINE_CHANNEL_ACCESS_TOKEN = 'EWhpPck/LwnxLR7g1ZXpNTDPCwZwMp8PnlZB7K+sGaP9JAeab7cq936bpmkTYLQHJzWliv6znbPNsNXeQEeKCqjerbRgg765sWZKg2OJdTmb9f9FOMSWBrTE8eQTKMuSb3mTtrkZ4zyyEunNAa/3AQdB04t89/1O/w1cDnyilFU='
LINE_CHANNEL_SECRET = '6b14d00ee2afeb1f5dba31c37a350c78'
OPENROUTER_API_KEY = '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'

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

openai.api_key = OPENROUTER_API_KEY
openai.api_base = "https://openrouter.ai/api/v1"
openai.api_type = "open_ai"

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_input = event.message.text
    system_prompt = "請幫助用戶用教育性語氣回應以下內容："

    try:
        response = openai.ChatCompletion.create(
            model="openai/gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ]
        )

        reply_text = response.choices[0].message["content"]
    except Exception as e:
        reply_text = f"發生錯誤：{e}"

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )
    
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
