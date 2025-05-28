from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from calendar_service import reserve_if_available


app = Flask(__name__)

# あなたのLINEチャネルの情報に書き換える
LINE_CHANNEL_ACCESS_TOKEN = 'wROGQyo4CCpnvpqAEqq0qN/BqH/SRLNX14mpmqqk5PZ34wWVy8fpSrY3ZIyI+QRPRZHlePUI6dn0NHgglhem/Ezj9AgnTvCK2UZ4RgjiRHbgC2IAVhG3U8ml4L/DK60bgjwQcIgRjLsGLU1Zgmok+wdB04t89/1O/w1cDnyilFU='
LINE_CHANNEL_SECRET = '60a62d1f213685b8648cebe00828e5d7'

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

@app.route("/callback", methods=['POST'])
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
    user_text = event.message.text
    user_id = event.source.user_id  # LINEユーザーID

    result = reserve_if_available(user_text, user_id)  # 引数追加

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=result)
    )



import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

