from flask import Flask, request, abort
import os
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from datetime import datetime
import pytz

app = Flask(__name__)

# 環境変数からLINEアクセストークンとシークレットを取得
line_bot_api = LineBotApi(os.environ["LINE_CHANNEL_ACCESS_TOKEN"])
handler = WebhookHandler(os.environ["LINE_CHANNEL_SECRET"])

# 進捗記録用の辞書（グループIDごと）
progress_log = {}

@app.route("/")
def hello_world():
    return "お前さんBot、起きてるぞ。"

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
    group_id = event.source.group_id if event.source.type == "group" else event.source.user_id
    text = event.message.text.strip()

    now = datetime.now(pytz.timezone("Asia/Tokyo"))
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")

    # 初期化
    if group_id not in progress_log:
        progress_log[group_id] = []

    # 発言があると記録
    progress_log[group_id].append((timestamp, text))

    if text.lower() == "進捗":
        msgs = [f"{t} - {msg}" for t, msg in progress_log[group_id]]
        response = "\n".join(msgs) if msgs else "進捗はまだ何もねぇぞ。"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=response))

    elif text.lower() == "まとめ":
        msgs = [f"{t} - {msg}" for t, msg in progress_log[group_id]]
        if msgs:
            note = "\n".join(msgs)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="今日の記録:\n" + note))
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="今日は何も喋ってねぇな。まとめるもんなんかねぇよ。"))

    elif text.lower() == "お前さん":
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="何だ。サボってんじゃねぇだろうな。"))

    else:
        # 建設的コメント（厳しめに）
        response = f"それで本気で前に進めるつもりか？甘えんなよ。内容次第では評価するが。"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=response))
        if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)