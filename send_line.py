#!/usr/bin/env python3
"""
LINE Messaging API で算数問題（問題のみ）を broadcast 送信するスクリプト
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

    if len(sys.argv) > 1:
        date = datetime.date.fromisoformat(sys.argv[1])
    else:
        date = datetime.date.today()

    text = gp.build_line_problem_text(date)
    send_broadcast(text, token)


if __name__ == "__main__":
    main()
