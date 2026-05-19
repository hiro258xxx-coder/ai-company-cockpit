"""
sync_cockpit.py — Claude Code セッション終了時・数字変更時に自動実行

やること:
  1. decision-log.md から最新3件の意思決定を抽出 → data.json に反映
  2. 変更前後を比較して history.json に差分を記録
  3. calendar.json を読んでカレンダーHTMLを生成
  4. data.json を git push → GitHub Pages が自動更新
"""

import json
import re
import subprocess
import datetime
import os
import copy

# ── パス設定 ──────────────────────────────────────────────────
COCKPIT_DIR   = r"C:\Users\lsbre\Desktop\AI参謀ツール\cockpit-cloud"
DATA_JSON     = os.path.join(COCKPIT_DIR, "data.json")
HISTORY_JSON  = os.path.join(COCKPIT_DIR, "history.json")
CALENDAR_JSON = os.path.join(COCKPIT_DIR, "calendar.json")
DECISION_LOG  = r"C:\Users\lsbre\.claude\ai-company\context\decisions\decision-log.md"


def parse_decisions(path, count=3):
    """decision-log.md から最新N件を抽出して返す"""
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        print(f"[SKIP] decision-log.md not found: {path}")
        return []

    decisions = []
    blocks = re.split(r"\n(?=### \d{4}-\d{2}-\d{2})", text)

    for block in blocks:
        date_m = re.match(r"### (\d{4}-\d{2}-\d{2})[｜|](.+)", block)
        if not date_m:
            continue

        date  = date_m.group(1).strip()
        title = date_m.group(2).strip()

        reason_m = re.search(r"\*\*判断理由\*\*\s*\n((?:- [^\n]+\n?)+)", block)
        reason = ""
        if reason_m:
            bullets = re.findall(r"- (.+)", reason_m.group(1))
            reason = "　".join(bullets[:2])

        decisions.append({"date": date, "title": title, "reason": reason})
        if len(decisions) >= count:
            break

    return decisions


# ── 1. data.json を読む（変更前コピーを保持）────────────────────
with open(DATA_JSON, encoding="utf-8") as f:
    data = json.load(f)
old_data = copy.deepcopy(data)

# ── 2. 意思決定を同期 ─────────────────────────────────────────
decisions = parse_decisions(DECISION_LOG)
if decisions:
    for i, dec in enumerate(decisions, 1):
        data[f"dec_{i}_date"]   = dec["date"]
        data[f"dec_{i}_title"]  = dec["title"]
        data[f"dec_{i}_reason"] = dec["reason"]
    print(f"[OK] {len(decisions)}件の意思決定を同期")
else:
    print("[SKIP] 意思決定の同期をスキップ（ファイルなし）")

# ── 3. 最終更新日を今日（JST）に ──────────────────────────────
jst = datetime.timezone(datetime.timedelta(hours=9))
now_jst = datetime.datetime.now(jst)
data["last_updated"] = now_jst.strftime("%Y-%m-%d")

# ── 3a. 変更履歴を記録 ────────────────────────────────────────
SKIP_KEYS = {"last_updated", "roi_gross", "roi_net", "calendar_html", "history_html"}
KEY_LABELS = {
    "cash": "手元資金", "mrr": "MRR", "cost": "月次固定費",
    "ai_hours": "AI削減工数", "ec_mrr": "EC MRR",
    "toolkit_mrr": "Toolkit MRR", "consult_clients": "コンサル成約数",
    "beargo_books": "BearGo冊数",
    "focus_1_title": "フォーカス1タイトル", "focus_1_desc": "フォーカス1詳細", "focus_1_dl": "フォーカス1期限",
    "focus_2_title": "フォーカス2タイトル", "focus_2_desc": "フォーカス2詳細", "focus_2_dl": "フォーカス2期限",
    "focus_3_title": "フォーカス3タイトル", "focus_3_desc": "フォーカス3詳細", "focus_3_dl": "フォーカス3期限",
    "dec_1_title": "意思決定1", "dec_2_title": "意思決定2", "dec_3_title": "意思決定3",
}

changes = []
for key, new_val in data.items():
    if key in SKIP_KEYS:
        continue
    old_val = old_data.get(key, "")
    if str(old_val) != str(new_val):
        label = KEY_LABELS.get(key, key)
        changes.append({"key": key, "label": label, "old": str(old_val), "new": str(new_val)})

try:
    with open(HISTORY_JSON, encoding="utf-8") as f:
        history = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    history = []

if changes:
    now_str = now_jst.strftime("%Y-%m-%d %H:%M")
    history.insert(0, {"datetime": now_str, "changes": changes})
    history = history[:30]
    with open(HISTORY_JSON, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)
    print(f"[OK] 変更履歴 {len(changes)}件を記録")
else:
    print("[OK] データ変更なし - 履歴追加スキップ")

# ── 3b. 変更履歴HTML生成 ──────────────────────────────────────
def gen_history_html(history):
    if not history:
        return '<div class="hist-empty">変更履歴はまだありません</div>'
    html = ""
    for entry in history[:10]:
        dt = entry.get("datetime", "")
        chg = entry.get("changes", [])
        items = ""
        for c in chg:
            label = c.get("label", c.get("key", ""))
            old   = c.get("old", "")
            new   = c.get("new", "")
            # Truncate long values for display
            if len(old) > 30:
                old = old[:28] + "…"
            if len(new) > 30:
                new = new[:28] + "…"
            items += (
                f'<div class="hist-chg">'
                f'<span class="hist-label">{label}</span>'
                f'<span class="hist-old">{old}</span>'
                f'<span class="hist-arr">&#8594;</span>'
                f'<span class="hist-new">{new}</span>'
                f'</div>'
            )
        html += f'<div class="hist-entry"><div class="hist-dt">{dt}</div>{items}</div>'
    return html

data["history_html"] = gen_history_html(history)

# ── 3c. カレンダーHTML生成 ────────────────────────────────────
try:
    with open(CALENDAR_JSON, encoding="utf-8") as f:
        calendar = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    calendar = []

def gen_calendar_html(calendar):
    if not calendar:
        return '<div class="cal-empty">カレンダーデータがありません（Claudeセッション中に更新されます）</div>'
    html = ""
    for day in calendar:
        date   = day.get("date", "")
        label  = day.get("label", "")
        events = day.get("events", [])
        is_today = label == "今日"

        badge   = '<span class="cal-today-badge">今日</span>' if is_today else ""
        day_cls = "cal-day today" if is_today else "cal-day"

        evs = ""
        for ev in events:
            time  = ev.get("time", "")
            title = ev.get("title", "")
            evs += (
                f'<div class="cal-ev">'
                f'<span class="cal-time">{time}</span>'
                f'<span class="cal-ttl">{title}</span>'
                f'</div>'
            )
        if not evs:
            evs = '<div class="cal-no-ev">予定なし</div>'

        html += (
            f'<div class="{day_cls}">'
            f'<div class="cal-date">{date}{badge}</div>'
            f'{evs}'
            f'</div>'
        )
    return html

data["calendar_html"] = gen_calendar_html(calendar)
print("[OK] カレンダーHTML生成完了")

# ── 4. data.json を保存 ───────────────────────────────────────
with open(DATA_JSON, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

# ── 5. generate.py を実行して index.html を再生成 ───────────────
import sys
subprocess.run([sys.executable, os.path.join(COCKPIT_DIR, "generate.py")], check=True, cwd=COCKPIT_DIR)

# ── 6. git push ───────────────────────────────────────────────
os.chdir(COCKPIT_DIR)
subprocess.run(["git", "add", "data.json", "history.json", "calendar.json", "index.html"], check=True)

result = subprocess.run(["git", "diff", "--staged", "--quiet"])
if result.returncode != 0:
    today = data["last_updated"]
    subprocess.run(
        ["git", "commit", "-m", f"Sync cockpit data {today}"],
        check=True
    )
    subprocess.run(["git", "push"], check=True)
    print(f"[OK] GitHub に push 完了 ({today})")
else:
    print("[OK] 変更なし — push スキップ")
