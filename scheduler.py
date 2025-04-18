import os
from linebot import LineBotApi
from linebot.models import TextSendMessage
from datetime import datetime
import pytz

line_bot_api = LineBotApi(os.environ["LINE_CHANNEL_ACCESS_TOKEN"])

# グループID一覧（本番では実際のIDに変更せよ）
group_ids = ["あなたのグループIDをここに入れる"]

# ダミー：記録ログ（本番はDBやファイル共有等で管理すべし）
progress_log = {
    "あなたのグループIDをここに入れる": [
        ("2025-04-18 12:00:00", "今日はじめてコード書いた"),
        ("2025-04-18 15:00:00", "お前さんと会話した")
    ]
}

def send_daily_summary():
    now = datetime.now(pytz.timezone("Asia/Tokyo"))
    today = now.strftime("%Y-%m-%d")
    for group_id in group_ids:
        logs = progress_log.get(group_id, [])
        today_logs = [f"{t} - {m}" for t, m in logs if t.startswith(today)]
        if today_logs:
            note = "\n".join(today_logs)
            message = f"{today} のまとめ:\n{note}"
        else:
            message = f"{today}は何も書かれてねぇ。何してたんだ？"
        line_bot_api.push_message(group_id, TextSendMessage(text=message))

if __name__ == "__main__":
    send_daily_summary()