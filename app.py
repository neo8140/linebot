from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = Flask(__name__)

# あなたのLINEチャネルの情報に書き換える
LINE_CHANNEL_ACCESS_TOKEN = 'wROGQyo4CCpnvpqAEqq0qN/BqH/SRLNX14mpmqqk5PZ34wWVy8fpSrY3ZIyI+QRPRZHlePUI6dn0NHgglhem/Ezj9AgnTvCK2UZ4RgjiRHbgC2IAVhG3U8ml4L/DK60bgjwQcIgRjLsGLU1Zgmok+wdB04t89/1O/w1cDnyilFU='
LINE_CHANNEL_SECRET = '60a62d1f213685b8648cebe00828e5d7'

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

@app.route("/webhook", methods=['POST'])
def webhook():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_msg = event.message.text
    reply_msg = f"ご予約内容『{user_msg}』を確認しました！"
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_msg))

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

