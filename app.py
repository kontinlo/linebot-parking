from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import requests

app = Flask(__name__)

# 設置你的 Line Bot Channel Access Token 和 Channel Secret
line_bot_api = LineBotApi('dGiRbQmLqhancFNwH71ahUwmjPzSKpjYrfo6vUsGKqhpj6LGpn6QQHxGvzxIjsu3k0d6FH0t+KV5wxzgWELVl2YqOsblF1w0BiPRek8dQ+QQaCXFRCuesCurwO4SsmN3Y6wGWsP3Y2lFcjGDsuSEQwdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('d14eeeda7ed631c0564e644a29060cf0')

@app.route("/callback", methods=['POST'])
def callback():
    # 從 Line 的請求中取得 X-Line-Signature
    signature = request.headers['X-Line-Signature']

    # 取得請求的 body
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        # 驗證簽名
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text

    # 使用 Nominatim API 查詢附近停車場
    response = requests.get(f'https://nominatim.openstreetmap.org/search?q={user_message}+parking&format=json&limit=1')
    result = response.json()
    if result:
        parking_location = result[0]
        address = parking_location['display_name']
        lat = parking_location['lat']
        lon = parking_location['lon']
        reply_text = f"附近的停車場位於: {address}\n地點: {lat}, {lon}\n[點擊這裡導航](https://www.google.com/maps/dir/?api=1&destination={lat},{lon})"
    else:
        reply_text = "抱歉，我找不到附近的停車場。"

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )

if __name__ == "__main__":
    app.run()
