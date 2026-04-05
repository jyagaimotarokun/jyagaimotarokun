"""
Vercel サーバーレス関数: LINE webhook ハンドラー
「できた」「出来た」「おわった」を受信したら今日の答えを返信する
"""
from http.server import BaseHTTPRequestHandler
import datetime
import json
import os
import sys
import urllib.request
import urllib.error

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import generate_problems as gp

JST = datetime.timezone(datetime.timedelta(hours=9))
TRIGGER_WORDS = {"できた", "出来た", "おわった", "終わった", "こたえ", "答え"}


def _jst_today() -> datetime.date:
    return datetime.datetime.now(JST).date()


def _reply(reply_token: str, text: str, token: str) -> None:
    url = "https://api.line.me/v2/bot/message/reply"
    payload = json.dumps({
        "replyToken": reply_token,
        "messages": [{"type": "text", "text": text}],
    }).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        },
        method="POST",
    )
    try:
        urllib.request.urlopen(req)
    except urllib.error.HTTPError as e:
        print(f"Reply failed: {e.code} {e.read().decode()}", file=sys.stderr)


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length))
        token = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN", "")

        for event in body.get("events", []):
            if event.get("type") != "message":
                continue
            if event["message"].get("type") != "text":
                continue

            text = event["message"]["text"].strip()
            reply_token = event.get("replyToken", "")

            if any(w in text for w in TRIGGER_WORDS):
                today = _jst_today()
                answer = gp.build_line_answer_text(today)
                _reply(reply_token, answer, token)

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

    def log_message(self, format, *args):
        pass  # ログ抑制
