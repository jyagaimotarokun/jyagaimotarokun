#!/usr/bin/env python3
"""
LINE Messaging API で算数問題を送信するスクリプト
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


def build_line_text(date: datetime.date) -> str:
    rng = gp.seeded_random(gp.get_seed(date))
    date_str = date.strftime("%-m月%-d日")

    lines = []
    lines.append(f"📚 {date_str}の さんすう もんだい")
    lines.append("今日も がんばろう！")
    lines.append("")

    lines.append("【1】けいさん (8もん)")
    calc_problems: list[tuple[str, str]] = []
    for _ in range(2):
        calc_problems.append(gp.addition_carry(rng))
    for _ in range(2):
        calc_problems.append(gp.subtraction_borrow(rng))
    for _ in range(2):
        calc_problems.append(gp.addition_within_100(rng))
    for _ in range(2):
        calc_problems.append(gp.subtraction_within_100(rng))
    rng.shuffle(calc_problems)
    for i, (q, _) in enumerate(calc_problems, 1):
        lines.append(f"({i}) {q} =")

    lines.append("")

    lines.append("【2】かけざん (5もん)")
    mult_problems: list[tuple[str, str]] = []
    for _ in range(5):
        mult_problems.append(gp.multiplication_table(rng))
    for i, (q, _) in enumerate(mult_problems, 1):
        lines.append(f"({i}) {q} =")

    lines.append("")

    lines.append("【3】ぶんしょうだい (4もん)")
    word_problems: list[tuple[str, str]] = []
    word_problems.append(gp.word_problem_addition(rng))
    word_problems.append(gp.word_problem_subtraction(rng))
    word_problems.append(gp.word_problem_multiplication(rng))
    word_problems.append(gp.word_problem_addition(rng))
    for i, (q, _) in enumerate(word_problems, 1):
        lines.append(f"({i}) {q}")

    lines.append("")

    lines.append("【4】とけい (1もん)")
    clock_q, clock_a = gp.clock_problem(rng)
    lines.append(f"(1) {clock_q}")

    lines.append("")

    lines.append("【5】ながさ (1もん)")
    len_q, len_a = gp.length_problem(rng)
    lines.append(f"(1) {len_q}")

    lines.append("")
    lines.append("▼ こたえ")

    lines.append("[けいさん]")
    for i, (q, a) in enumerate(calc_problems, 1):
        lines.append(f"({i}) {q} = {a}")

    lines.append("[かけざん]")
    for i, (q, a) in enumerate(mult_problems, 1):
        lines.append(f"({i}) {q} = {a}")

    lines.append("[ぶんしょうだい]")
    for i, (_, a) in enumerate(word_problems, 1):
        lines.append(f"({i}) {a}")

    lines.append(f"[とけい] (1) {clock_a}")
    lines.append(f"[ながさ] (1) {len_a}")

    return "
".join(lines)


def send_line_message(text: str, token: str) -> None:
    url = "https://api.line.me/v2/bot/message/broadcast"
    payload = json.dumps({
        "messages": [{"type": "text", "text": text}]
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

    text = build_line_text(date)
    send_line_message(text, token)


if __name__ == "__main__":
    main()
