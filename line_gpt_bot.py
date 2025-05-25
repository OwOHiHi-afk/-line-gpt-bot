from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import openai
import os

app = Flask(__name__)

# ==== LINE credentials ====
LINE_CHANNEL_ACCESS_TOKEN = 'EWhpPck/LwnxLR7g1ZXpNTDPCwZwMp8PnlZB7K+sGaP9JAeab7cq936bp...'
LINE_CHANNEL_SECRET = '6b14d00ee2afeb1f5dba31c37a350c78'

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# ==== OpenRouter API key ====
openai.api_key = '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'
openai.api_base = 'https://openrouter.ai/api/v1'  # 指定 OpenRouter

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except Exception as e:
        print(f"[ERROR] {e}")
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_input = event.message.text

    system_prompt = "你是一位網路法律教育講師，幫助使用者識別網路互動中的法律風險。請產生 1 個情境模擬（2 句），選項（3～4個+附emoji），每個選項的風險簡要說明，不要冗長。"

    try:
        response = openai.ChatCompletion.create(
            model="openai/gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ]
        )
        reply_text = response['choices'][0]['message']['content']
    except Exception as e:
        reply_text = f"⚠️ 系統錯誤：{str(e)}"

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
