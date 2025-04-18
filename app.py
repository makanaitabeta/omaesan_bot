from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os
import openai

app = Flask(__name__)

# 環境変数から設定を取得
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# LINE Botの設定
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# OpenAI APIキーを設定
openai.api_key = OPENAI_API_KEY

@app.route("/")
def index():
    return "おまえさんBot、地獄から起動中。"

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
    user_message = event.message.text

    # ChatGPTへのプロンプトにおまえさんのキャラを反映
    prompt = f"""
ユーザーからの質問: 「{user_message}」

おまえさんBotとして以下のように答えろ：
- 超厳しい
- でも的を射たアドバイス
- 甘えや迷いは全否定
- 建設的で前に進ませる
- ユーモアも忘れるな

おまえさんの返答：
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "あなたは超厳しくも愛のあるアドバイザー『おまえさん』です。"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.8,
        )

        reply_text = response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        reply_text = f"エラーだ。理由？そんなもん自分で調べろ。詳細: {str(e)}"

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Render用にPORT環境変数使う
    app.run(host="0.0.0.0", port=port)