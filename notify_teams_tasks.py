#!/usr/bin/env python3
"""
Microsoft Teams タスク期限通知スクリプト
今週中に期限を迎える Planner タスクを担当者宛に Teams チャンネルへ通知する。

必要な環境変数:
  MS_TENANT_ID        : Azure AD テナント ID
  MS_CLIENT_ID        : アプリのクライアント ID
  MS_CLIENT_SECRET    : アプリのクライアントシークレット
  MS_PLANNER_PLAN_ID  : 対象 Planner プラン ID
  MS_TEAMS_TEAM_ID    : 通知先 Teams チーム ID
  MS_TEAMS_CHANNEL_ID : 通知先チャンネル ID
"""
import datetime
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

GRAPH_BASE = "https://graph.microsoft.com/v1.0"


def get_access_token(tenant_id: str, client_id: str, client_secret: str) -> str:
    """OAuth2 クライアント認証フローでアクセストークンを取得する。"""
    url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    data = urllib.parse.urlencode({
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": "https://graph.microsoft.com/.default",
    }).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())["access_token"]


def graph_get(path: str, token: str) -> Any:
    """Microsoft Graph API の GET リクエストを実行する。"""
    req = urllib.request.Request(
        f"{GRAPH_BASE}{path}",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def this_week_range() -> tuple[datetime.date, datetime.date]:
    """今週の月曜日から日曜日の範囲を返す。"""
    today = datetime.date.today()
    monday = today - datetime.timedelta(days=today.weekday())
    sunday = monday + datetime.timedelta(days=6)
    return monday, sunday


def tasks_due_this_week(plan_id: str, token: str) -> list[dict]:
    """今週中に期限を迎える未完了タスクの一覧を返す。"""
    monday, sunday = this_week_range()
    data = graph_get(f"/planner/plans/{plan_id}/tasks", token)
    result = []
    for task in data.get("value", []):
        if task.get("percentComplete", 0) == 100:
            continue
        due_str = task.get("dueDateTime")
        if not due_str:
            continue
        due_date = datetime.date.fromisoformat(due_str[:10])
        if monday <= due_date <= sunday:
            result.append(task)
    return result


def get_user(user_id: str, token: str) -> dict:
    """ユーザーの表示名などを取得する。失敗時はIDのみ返す。"""
    try:
        return graph_get(f"/users/{user_id}?$select=id,displayName", token)
    except urllib.error.HTTPError:
        return {"id": user_id, "displayName": user_id}


def build_message(
    tasks: list[dict],
    user_cache: dict[str, dict],
) -> dict:
    """Teamsチャンネルへ POST する JSON ペイロードを組み立てる。"""
    today = datetime.date.today()
    monday, sunday = this_week_range()
    week_label = f"{monday.month}/{monday.day}（月）〜{sunday.month}/{sunday.day}（日）"

    # @メンション情報を構築
    mentions: list[dict] = []
    mention_idx: dict[str, int] = {}
    for task in tasks:
        for uid in task.get("assignments", {}).keys():
            if uid not in mention_idx:
                idx = len(mentions)
                mention_idx[uid] = idx
                user = user_cache.get(uid, {"id": uid, "displayName": uid})
                mentions.append({
                    "id": idx,
                    "mentionText": user["displayName"],
                    "mentioned": {
                        "user": {
                            "id": uid,
                            "displayName": user["displayName"],
                            "userIdentityType": "aadUser",
                        }
                    },
                })

    # 担当者ごとにタスクをグループ化
    by_user: dict[str, list[dict]] = {}
    unassigned: list[dict] = []
    for task in sorted(tasks, key=lambda t: t.get("dueDateTime", "")):
        assignees = list(task.get("assignments", {}).keys())
        if not assignees:
            unassigned.append(task)
        else:
            for uid in assignees:
                by_user.setdefault(uid, []).append(task)

    def urgency(due: datetime.date) -> str:
        days = (due - today).days
        if days <= 1:
            return "🔴"
        if days <= 3:
            return "🟡"
        return "🟢"

    lines = [f"<b>📋 今週({week_label})期限のタスク通知</b><br>"]

    for uid, user_tasks in by_user.items():
        idx = mention_idx[uid]
        name = user_cache.get(uid, {}).get("displayName", uid)
        lines.append(f'<at id="{idx}">{name}</at> さんの担当タスク:<br>')
        for task in user_tasks:
            due = datetime.date.fromisoformat(task["dueDateTime"][:10])
            lines.append(
                f"　{urgency(due)} {task['title']}（期限: {due.month}/{due.day}）<br>"
            )
        lines.append("<br>")

    if unassigned:
        lines.append("担当者未設定のタスク:<br>")
        for task in unassigned:
            due = datetime.date.fromisoformat(task["dueDateTime"][:10])
            lines.append(
                f"　{urgency(due)} {task['title']}（期限: {due.month}/{due.day}）<br>"
            )

    return {
        "body": {"contentType": "html", "content": "\n".join(lines)},
        "mentions": mentions,
    }


def post_channel_message(team_id: str, channel_id: str, token: str, payload: dict) -> None:
    """Teams チャンネルにメッセージを投稿する。"""
    url = f"{GRAPH_BASE}/teams/{team_id}/channels/{channel_id}/messages"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as resp:
            print(f"Teams 送信成功: HTTP {resp.status}")
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        print(f"Teams 送信失敗: HTTP {e.code} - {body}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    env = {
        "MS_TENANT_ID": os.environ.get("MS_TENANT_ID", ""),
        "MS_CLIENT_ID": os.environ.get("MS_CLIENT_ID", ""),
        "MS_CLIENT_SECRET": os.environ.get("MS_CLIENT_SECRET", ""),
        "MS_PLANNER_PLAN_ID": os.environ.get("MS_PLANNER_PLAN_ID", ""),
        "MS_TEAMS_TEAM_ID": os.environ.get("MS_TEAMS_TEAM_ID", ""),
        "MS_TEAMS_CHANNEL_ID": os.environ.get("MS_TEAMS_CHANNEL_ID", ""),
    }
    missing = [k for k, v in env.items() if not v]
    if missing:
        print(f"エラー: 環境変数が未設定です: {', '.join(missing)}", file=sys.stderr)
        sys.exit(1)

    print("アクセストークンを取得中...")
    token = get_access_token(env["MS_TENANT_ID"], env["MS_CLIENT_ID"], env["MS_CLIENT_SECRET"])

    print("今週期限のタスクを取得中...")
    tasks = tasks_due_this_week(env["MS_PLANNER_PLAN_ID"], token)

    if not tasks:
        print("今週期限のタスクはありません。通知をスキップします。")
        return

    print(f"対象タスク: {len(tasks)} 件")

    user_ids: set[str] = set()
    for task in tasks:
        user_ids.update(task.get("assignments", {}).keys())

    user_cache: dict[str, dict] = {}
    for uid in user_ids:
        info = get_user(uid, token)
        user_cache[uid] = info
        print(f"  ユーザー取得: {info.get('displayName', uid)}")

    payload = build_message(tasks, user_cache)

    print("Teams に通知を送信中...")
    post_channel_message(
        env["MS_TEAMS_TEAM_ID"],
        env["MS_TEAMS_CHANNEL_ID"],
        token,
        payload,
    )


if __name__ == "__main__":
    main()
