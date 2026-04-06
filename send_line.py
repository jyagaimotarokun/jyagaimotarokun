#!/usr/bin/env python3
"""
LINE Messaging API で broadcast 送信するスクリプト
使い方:
  python send_line.py [日付]           # 問題を送信
  python send_line.py [日付] --answers # 答えを送信
環境変数:
  LINE_CHANNEL_ACCESS_TOKEN: チャネルアクセストークン
"""
import datetime
import os
import sys
import urllib.request
import urllib.error
import json

import generate_problems as gp


def send_broadcast(text: str, token: str) -> None:
    url = "https://api.line.me/v2/bot/message/broadcast"
    payload = json.dumps(
        {"messages": [{"type": "text", "text": text}]}
    ).encode("utf-8")
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
        with urllib.request.urlopen(req) as resp:
            print(f"LINE 送信成功: HTTP {resp.status}")
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        print(f"LINE 送信失敗: HTTP {e.code} - {body}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    token = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
    if not token:
        print(
            "エラー: 環境変数 LINE_CHANNEL_ACCESS_TOKEN を設定してください",
            file=sys.stderr,
        )
        sys.exit(1)

    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    answers_mode = "--answers" in sys.argv

    date = datetime.date.fromisoformat(args[0]) if args else datetime.date.today()

    if answers_mode:
        text = gp.build_line_answer_text(date)
    else:
        text = gp.build_line_problem_text(date)

    send_broadcast(text, token)


if __name__ == "__main__":
    main()
