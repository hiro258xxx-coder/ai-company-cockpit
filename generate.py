"""
cockpit 自動生成スクリプト — K-Cockpit v2 司令塔スタイル
  - data.json を読む
  - last_updated を今日（JST）に更新
  - ROI・各種HTML を自動計算
  - index.html を生成
"""

import json
import datetime
import os

# ── 1. データ読み込み ──────────────────────────────────────────
with open("data.json", encoding="utf-8") as f:
    data = json.load(f)

# ── 2. 日付を今日（JST）に更新 ────────────────────────────────
jst = datetime.timezone(datetime.timedelta(hours=9))
data["last_updated"] = datetime.datetime.now(jst).strftime("%Y-%m-%d")

# ── 3. ROI 自動計算 ───────────────────────────────────────────
ai_h = int(str(data.get("ai_hours", "144")).replace(",", ""))
cost = int(str(data.get("cost", "30000")).replace(",", ""))
data["roi_gross"] = f"{ai_h * 2000:,}"
data["roi_net"]   = f"{ai_h * 2000 - cost:,}"

# ── 4. プロジェクト別 Next 3 Steps HTML ───────────────────────
def gen_nexts_html(raw):
    items = [s.strip() for s in raw.split("|") if s.strip()]
    html = ""
    for i, item in enumerate(items[:3]):
        html += (
            f'<div class="ni">'
            f'<span class="ni-n">{i + 1}</span>'
            f'<span class="ni-t">{item}</span>'
            f'</div>'
        )
    return html or '<div class="ni"><span class="ni-t" style="color:var(--tm)">—</span></div>'

for proj in ["ec", "toolkit", "consult", "beargo", "minecraft", "diary"]:
    raw = data.get(f"{proj}_next", "")
    data[f"{proj}_nexts_html"] = gen_nexts_html(raw)

# ── 5. 収益目標 進捗バー HTML ─────────────────────────────────
def pct(cur_str, tgt_str):
    try:
        c = float(str(cur_str).replace(",", "").replace("–", "0").replace("-", "0"))
        t = float(str(tgt_str).replace(",", ""))
        return min(100, round(c / t * 100)) if t > 0 else 0
    except Exception:
        return 0

data["ec_pct"]      = str(pct(data.get("ec_mrr", "0"),      data.get("ec_mrr_target", "300000")))
data["toolkit_pct"] = str(pct(data.get("toolkit_mrr", "0"), data.get("toolkit_mrr_target", "100000")))
data["consult_pct"] = str(pct(data.get("consult_mrr", "0"), data.get("consult_mrr_target", "300000")))
data["beargo_pct"]  = str(pct(data.get("beargo_mrr", "0"),  data.get("beargo_mrr_target", "100000")))
data["salary_pct"]  = str(pct(data.get("salary", "0"),       data.get("salary_target", "500000")))

# ── 6. data.json を保存（日付更新を反映）──────────────────────
with open("data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

# ── 7. HTML テンプレート ──────────────────────────────────────
TEMPLATE = """\
<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>K-Cockpit | 岩嵜 AI カンパニー 統合司令室</title>
  <style>
    :root {
      --bg:#08080f;--s1:#0f0f1c;--s2:#161626;--s3:#1e1e30;
      --border:#252538;--bl:#333350;
      --purple:#8b6fff;--pl:#b09aff;--pdim:rgba(139,111,255,.12);
      --green:#4ade80;--gdim:rgba(74,222,128,.1);
      --yellow:#fbbf24;--ydim:rgba(251,191,36,.1);
      --blue:#38bdf8;--bdim:rgba(56,189,248,.1);
      --teal:#2dd4bf;
      --text:#dcdcf0;--td:#a0a0c4;--tm:#6a6a90;
      --r:14px;
    }
    *,*::before,*::after{margin:0;padding:0;box-sizing:border-box}
    body{background:var(--bg);color:var(--text);
      font-family:'Helvetica Neue',Arial,'Hiragino Kaku Gothic ProN','Yu Gothic',sans-serif;
      min-height:100vh;padding:24px 36px 64px}

    /* ── Animations ── */
    @keyframes fadeUp{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:none}}
    @keyframes pulse{0%,100%{box-shadow:0 0 0 0 rgba(74,222,128,.5)}50%{box-shadow:0 0 0 7px rgba(74,222,128,0)}}
    @keyframes shimmer{0%{background-position:-200% center}100%{background-position:200% center}}
    @keyframes scan{0%{left:-35%}100%{left:110%}}
    @keyframes bounce{0%,100%{transform:scale(1)}40%{transform:scale(1.28)}}
    @keyframes glow{0%,100%{opacity:.5}50%{opacity:1}}
    .fade-in{animation:fadeUp .45s ease both}
    .d1{animation-delay:.05s}.d2{animation-delay:.1s}.d3{animation-delay:.16s}
    .d4{animation-delay:.22s}.d5{animation-delay:.28s}
    .emoji-bounce{animation:bounce .3s ease}

    /* ── Cards ── */
    .card{background:var(--s1);border:1px solid var(--border);border-radius:var(--r);
      transition:transform .2s,border-color .2s,box-shadow .2s}
    .card:hover{transform:translateY(-2px);border-color:var(--bl);box-shadow:0 8px 32px rgba(0,0,0,.5)}
    .pro-card{border-color:rgba(139,111,255,.2)}
    .pro-card:hover{border-color:rgba(139,111,255,.45);box-shadow:0 8px 32px rgba(139,111,255,.12)}
    .personal-card{border-color:rgba(56,189,248,.18)}
    .personal-card:hover{border-color:rgba(56,189,248,.4);box-shadow:0 8px 32px rgba(56,189,248,.1)}

    /* ── Hero ── */
    .hero{
      position:relative;min-height:440px;margin-bottom:24px;
      border-radius:20px;overflow:hidden;
      display:flex;flex-direction:column;justify-content:space-between;
      background:
        linear-gradient(to bottom,
          rgba(8,8,15,.82) 0%,
          rgba(8,8,15,.05) 30%,
          rgba(8,8,15,.05) 58%,
          rgba(8,8,15,.94) 100%),
        url('images/commander.png') center top / cover no-repeat,
        #08080f;
      border:1px solid rgba(56,189,248,.22)}
    .hero::before{
      content:'';position:absolute;top:0;left:0;right:0;height:1px;z-index:5;
      background:linear-gradient(90deg,transparent,rgba(56,189,248,.7),rgba(139,111,255,.6),transparent)}
    .hero::after{
      content:'';position:absolute;top:0;width:32%;height:100%;z-index:5;
      background:linear-gradient(90deg,transparent,rgba(56,189,248,.04),transparent);
      animation:scan 10s linear infinite;pointer-events:none}
    /* Hero top bar */
    .hero-top{
      display:flex;justify-content:space-between;align-items:flex-start;
      padding:22px 28px;position:relative;z-index:6}
    .hero-brand{
      font-size:11px;font-weight:700;letter-spacing:.15em;text-transform:uppercase;
      color:var(--blue);display:flex;align-items:center;gap:8px;margin-bottom:6px}
    .hero-brand::before{content:'◈';font-size:9px;animation:glow 2s ease infinite}
    .hero-top-status{display:flex;align-items:center;gap:6px;font-size:11px;color:var(--td)}
    .status-pulse{width:7px;height:7px;border-radius:50%;background:var(--green);
      animation:pulse 2s infinite;display:inline-block;flex-shrink:0}
    /* Hero meta (top-right) */
    .hero-meta-wrap{text-align:right;flex-shrink:0}
    .hero-updated{font-size:11px;color:var(--td)}
    .hero-auto{display:inline-flex;align-items:center;gap:4px;font-size:10px;
      background:rgba(139,111,255,.12);color:var(--pl);
      padding:2px 8px;border-radius:8px;margin-top:3px}
    .hero-edit{display:inline-block;font-size:11px;color:var(--purple);margin-top:4px;text-decoration:none}
    .hero-edit:hover{text-decoration:underline}
    /* Hero bottom */
    .hero-bottom{padding:0 28px 24px;position:relative;z-index:6}
    .hero-name{font-size:32px;font-weight:900;color:#fff;letter-spacing:-.02em;line-height:1;margin-bottom:3px}
    .hero-role{font-size:12px;color:var(--td);margin-bottom:18px}
    /* Metric chips */
    .hero-metrics{display:flex;gap:10px;flex-wrap:wrap}
    .hero-metric{
      flex:1;min-width:135px;
      padding:14px 18px;border-radius:14px;
      background:rgba(8,8,15,.58);
      backdrop-filter:blur(18px);-webkit-backdrop-filter:blur(18px);
      border:1px solid rgba(255,255,255,.1)}
    .hm-label{font-size:10px;color:var(--td);font-weight:600;
      letter-spacing:.06em;margin-bottom:7px}
    .hm-value{font-size:26px;font-weight:900;color:#fff;line-height:1}
    .hm-sub{font-size:10px;color:var(--green);margin-top:5px;font-weight:600}
    .hm-note{font-size:10px;color:var(--tm);margin-top:4px}
    .hm-ai .hm-value{color:var(--green)}

    /* ── Theme switcher ── */
    .th-wrap{margin-top:8px}
    .th-label-text{font-size:9px;color:var(--tm);text-align:right;margin-bottom:3px}
    .theme-switcher{display:flex;gap:5px;justify-content:flex-end}
    .th-btn{width:30px;height:30px;border-radius:8px;border:1px solid var(--border);
      background:var(--s2);color:var(--td);font-size:14px;cursor:pointer;
      display:flex;align-items:center;justify-content:center;
      transition:all .2s;opacity:.5;line-height:1}
    .th-btn:hover{opacity:1;transform:scale(1.12);border-color:var(--bl)}
    .th-btn.active{opacity:1;border-color:var(--blue);background:var(--bdim)}

    /* ── Section ── */
    .section{margin-bottom:28px}
    .sec-title{font-size:10px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;
      color:var(--tm);margin-bottom:14px;display:flex;align-items:center;gap:10px}
    .sec-title::after{content:'';flex:1;height:1px;background:var(--border)}
    .sec-cat-badge{font-size:9px;font-weight:700;padding:2px 8px;border-radius:6px;
      letter-spacing:.05em;text-transform:none}
    .badge-pro{background:rgba(139,111,255,.12);color:var(--pl);border:1px solid rgba(139,111,255,.2)}
    .badge-personal{background:rgba(56,189,248,.1);color:#7dd3fc;border:1px solid rgba(56,189,248,.18)}

    /* ── Financial Targets ── */
    .fin-grid{display:grid;grid-template-columns:repeat(5,1fr);gap:12px}
    .fin-card{padding:16px 18px}
    .fin-label{font-size:10px;color:var(--td);margin-bottom:6px}
    .fin-val{font-size:20px;font-weight:900;color:#fff;line-height:1}
    .fin-target{font-size:10px;color:var(--tm);margin-top:5px}
    .fin-bar{height:3px;background:var(--border);border-radius:3px;margin-top:8px;overflow:hidden}
    .fin-fill{height:100%;border-radius:3px;background:linear-gradient(90deg,var(--purple),var(--pl));transition:width 1s ease}
    .fin-fill.green{background:linear-gradient(90deg,#22c55e,#4ade80)}
    .fin-fill.blue{background:linear-gradient(90deg,#0ea5e9,#38bdf8)}

    /* ── Project ── */
    .project-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}
    .project-card{padding:20px}
    .cat-tag{display:inline-flex;align-items:center;gap:4px;font-size:9px;font-weight:700;
      padding:2px 7px;border-radius:5px;margin-bottom:12px;text-transform:uppercase;letter-spacing:.06em}
    .tag-pro{background:rgba(139,111,255,.12);color:var(--pl);border:1px solid rgba(139,111,255,.2)}
    .tag-personal{background:rgba(56,189,248,.1);color:#7dd3fc;border:1px solid rgba(56,189,248,.18)}
    .emoji-wrap{position:relative;display:inline-flex;align-items:center;justify-content:center;
      width:48px;height:48px;background:var(--s2);border-radius:12px;
      font-size:26px;cursor:pointer;user-select:none;margin-bottom:12px;
      transition:background .2s,transform .15s}
    .emoji-wrap:hover{background:var(--s3);transform:scale(1.08)}
    .emoji-wrap:active{transform:scale(.93)}
    .emoji-hint{position:absolute;bottom:-4px;right:-4px;font-size:8px;
      background:var(--border);color:var(--td);border-radius:5px;padding:1px 4px}
    .emoji-picker{display:none;position:absolute;top:72px;left:0;z-index:200;
      background:var(--s2);border:1px solid var(--bl);border-radius:12px;
      padding:10px;box-shadow:0 20px 60px rgba(0,0,0,.7);
      grid-template-columns:repeat(4,1fr);gap:4px}
    .emoji-picker.open{display:grid}
    .ep-opt{font-size:22px;width:38px;height:38px;display:flex;align-items:center;
      justify-content:center;border-radius:8px;cursor:pointer;transition:background .15s}
    .ep-opt:hover{background:var(--s3)}
    .pj-row{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px}
    .pj-name{font-size:15px;font-weight:700;color:#fff}
    .pj-sub{font-size:10px;color:var(--tm);margin-top:2px;line-height:1.4}
    .badge{display:inline-flex;align-items:center;gap:4px;font-size:10px;font-weight:700;
      padding:3px 9px;border-radius:18px;white-space:nowrap}
    .bdot{width:5px;height:5px;border-radius:50%}
    .b-active{background:var(--gdim);color:var(--green);border:1px solid rgba(74,222,128,.25)}
    .b-active .bdot{background:var(--green);animation:pulse 1.8s infinite}
    .b-build{background:var(--ydim);color:var(--yellow);border:1px solid rgba(251,191,36,.25)}
    .b-build .bdot{background:var(--yellow)}
    .b-ready{background:var(--pdim);color:var(--pl);border:1px solid rgba(167,139,250,.25)}
    .b-ready .bdot{background:var(--pl)}
    .pj-metric{font-size:26px;font-weight:900;color:#fff;line-height:1;margin-bottom:2px}
    .pj-metric-label{font-size:10px;color:var(--tm);margin-bottom:8px}
    .prog-bar{height:4px;background:var(--border);border-radius:4px;margin-bottom:12px;overflow:hidden}
    .prog-fill{height:100%;border-radius:4px;transition:width .8s cubic-bezier(.4,0,.2,1)}
    .fill-green{background:linear-gradient(90deg,#22c55e,#4ade80)}
    .fill-yellow{background:linear-gradient(90deg,#d97706,#fbbf24)}
    .fill-purple{background:linear-gradient(90deg,#7c3aed,#a78bfa)}
    .fill-teal{background:linear-gradient(90deg,#0d9488,#2dd4bf)}
    .fill-blue{background:linear-gradient(90deg,#0ea5e9,#38bdf8)}
    .ni{display:flex;align-items:baseline;gap:7px;padding:5px 0;
      border-bottom:1px solid rgba(37,37,56,.8)}
    .ni:last-child{border-bottom:none}
    .ni-n{font-size:9px;font-weight:900;color:var(--purple);min-width:12px;flex-shrink:0}
    .ni-t{font-size:11px;color:var(--td);line-height:1.4}

    /* ── Automation ── */
    .auto-grid{display:grid;grid-template-columns:3fr 2fr;gap:12px}
    .auto-panel{padding:20px 22px}
    .auto-title{font-size:13px;font-weight:700;color:#fff;margin-bottom:16px;
      display:flex;align-items:center;gap:8px}
    .dot-pulse{width:7px;height:7px;border-radius:50%;background:var(--green);animation:pulse 1.8s infinite}
    .dot-idle{width:7px;height:7px;border-radius:50%;background:var(--yellow)}
    .auto-row{display:flex;justify-content:space-between;align-items:center;
      padding:10px 0;border-bottom:1px solid var(--border)}
    .auto-row:last-child{border-bottom:none}
    .auto-name{font-size:12px;color:var(--text)}
    .auto-tech{font-size:10px;color:var(--tm);margin-top:2px}
    .auto-save{font-size:11px;font-weight:700;color:var(--green)}
    .wip-badge{font-size:9px;font-weight:700;padding:2px 8px;border-radius:18px;
      background:var(--ydim);color:var(--yellow);border:1px solid rgba(251,191,36,.2)}
    .roi-box{margin-top:18px;padding:16px;
      background:linear-gradient(135deg,var(--s2) 0%,rgba(139,111,255,.07) 100%);
      border:1px solid rgba(139,111,255,.22);border-radius:12px}
    .roi-box-label{font-size:10px;color:var(--tm);margin-bottom:5px}
    .roi-box-val{font-size:20px;font-weight:900;color:#fff}
    .roi-box-sub{font-size:10px;color:var(--tm);margin-top:3px}
    .roi-box-net{font-size:18px;font-weight:900;color:var(--green);margin-top:10px}

    /* ── Two-col ── */
    .two-col{display:grid;grid-template-columns:1fr 1fr;gap:20px}
    .focus-item{display:flex;align-items:flex-start;gap:14px;padding:16px;
      margin-bottom:8px;transition:transform .2s,border-color .2s}
    .focus-item:hover{transform:translateX(4px);border-color:var(--bl)}
    .focus-num{font-size:26px;font-weight:900;color:var(--purple);line-height:1;min-width:22px}
    .focus-body{flex:1}
    .focus-ttl{font-size:13px;font-weight:700;color:#fff}
    .focus-desc{font-size:11px;color:var(--td);margin-top:3px;line-height:1.55}
    .focus-dl{font-size:10px;font-weight:700;color:var(--yellow);
      background:var(--ydim);padding:2px 9px;border-radius:10px;white-space:nowrap}
    .dec-item{padding:16px 18px;margin-bottom:8px;transition:border-color .2s}
    .dec-item:hover{border-color:var(--bl)}
    .dec-date{font-size:10px;color:var(--tm);margin-bottom:4px}
    .dec-title{font-size:13px;font-weight:700;color:#fff;margin-bottom:5px}
    .dec-reason{font-size:11px;color:var(--td);line-height:1.6}

    /* ── Calendar ── */
    .cal-strip{margin-bottom:22px}
    .cal-strip-label{font-size:10px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;
      color:var(--tm);margin-bottom:10px;display:flex;align-items:center;gap:10px}
    .cal-strip-label::after{content:'';flex:1;height:1px;background:var(--border)}
    .cal-scroll{display:flex;gap:10px;overflow-x:auto;padding-bottom:6px;scroll-snap-type:x mandatory}
    .cal-scroll::-webkit-scrollbar{height:3px}
    .cal-scroll::-webkit-scrollbar-track{background:transparent}
    .cal-scroll::-webkit-scrollbar-thumb{background:var(--border);border-radius:2px}
    .cal-day{flex:0 0 180px;scroll-snap-align:start;padding:12px 14px;background:var(--s1);
      border:1px solid var(--border);border-radius:12px;
      max-height:190px;overflow-y:auto;display:flex;flex-direction:column}
    .cal-day::-webkit-scrollbar{width:2px}
    .cal-day::-webkit-scrollbar-thumb{background:var(--border);border-radius:1px}
    .cal-day.today{flex:0 0 210px;border-color:rgba(56,189,248,.45);
      background:linear-gradient(135deg,var(--s1),rgba(56,189,248,.05))}
    .cal-day:hover{border-color:var(--bl)}
    .cal-date{font-size:11px;font-weight:700;color:var(--blue);margin-bottom:7px;
      display:flex;align-items:center;gap:5px;flex-shrink:0}
    .cal-today-badge{font-size:8px;font-weight:700;background:var(--blue);color:#000;
      padding:1px 6px;border-radius:5px}
    .cal-ev{display:flex;gap:6px;padding:4px 0;border-bottom:1px solid rgba(37,37,56,.7)}
    .cal-ev:last-child{border-bottom:none}
    .cal-time{font-size:9px;color:var(--tm);min-width:34px;flex-shrink:0;padding-top:1px}
    .cal-ttl{font-size:11px;color:var(--text);line-height:1.4}
    .cal-no-ev{font-size:11px;color:var(--tm)}
    .cal-empty{font-size:12px;color:var(--tm);padding:14px 0}

    /* ── History ── */
    .hist-list{display:grid;gap:8px}
    .hist-entry{padding:12px 16px;background:var(--s1);border:1px solid var(--border);
      border-radius:10px;transition:border-color .2s}
    .hist-entry:hover{border-color:var(--bl)}
    .hist-dt{font-size:10px;color:var(--tm);font-weight:700;margin-bottom:6px}
    .hist-chg{display:flex;align-items:center;gap:7px;margin-bottom:3px;flex-wrap:wrap}
    .hist-label{font-size:10px;font-weight:700;color:var(--pl);min-width:100px}
    .hist-old{font-size:10px;color:var(--tm);text-decoration:line-through;
      max-width:130px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
    .hist-arr{font-size:10px;color:var(--tm)}
    .hist-new{font-size:10px;color:var(--green);font-weight:600}
    .hist-empty{font-size:12px;color:var(--tm);padding:18px 0;text-align:center}

    /* ── Footer ── */
    .footer{margin-top:48px;padding-top:18px;border-top:1px solid var(--border);
      text-align:center;font-size:10px;color:var(--tm)}

    /* ── Responsive ── */
    @media(max-width:1200px){.fin-grid{grid-template-columns:repeat(2,1fr)}}
    @media(max-width:900px){body{padding:16px}.project-grid{grid-template-columns:repeat(2,1fr)}.auto-grid{grid-template-columns:1fr}.two-col{grid-template-columns:1fr}.hero-metrics{gap:8px}}
    @media(max-width:600px){.project-grid{grid-template-columns:1fr}.fin-grid{grid-template-columns:1fr 1fr}.hero{min-height:360px}.hm-value{font-size:20px}}

    /* ── Theme Variables ── */
    [data-theme="architect"]{
      --bg:#050a18;--s1:#080f25;--s2:#0c1430;--s3:#111a3a;
      --border:#182040;--bl:#243060;
      --purple:#5577ee;--pl:#88aaff;--pdim:rgba(85,119,238,.12);
      --green:#3ac88a;--gdim:rgba(58,200,138,.1);
      --yellow:#f0c040;--ydim:rgba(240,192,64,.1);
      --blue:#55aaff;--bdim:rgba(85,170,255,.1);
      --teal:#30c0b0;
      --text:#c8d8f0;--td:#8899cc;--tm:#4a5878;
    }
    [data-theme="strategist"]{
      --bg:#f0f0ea;--s1:#ffffff;--s2:#f5f5f0;--s3:#eaeae3;
      --border:#d8d8d0;--bl:#b8b8a8;
      --purple:#5a3a8a;--pl:#7a5aaa;--pdim:rgba(90,58,138,.1);
      --green:#2a7040;--gdim:rgba(42,112,64,.1);
      --yellow:#8a6010;--ydim:rgba(138,96,16,.1);
      --blue:#1a508a;--bdim:rgba(26,80,138,.1);
      --teal:#1a706a;
      --text:#18182a;--td:#44445a;--tm:#888898;
    }
    [data-theme="investor"]{
      --bg:#090908;--s1:#111110;--s2:#181815;--s3:#1e1e1a;
      --border:#262620;--bl:#363630;
      --purple:#c89018;--pl:#e0b838;--pdim:rgba(200,144,24,.12);
      --green:#2aba5a;--gdim:rgba(42,186,90,.08);
      --yellow:#e0a820;--ydim:rgba(224,168,32,.1);
      --blue:#3a8858;--bdim:rgba(58,136,88,.08);
      --teal:#38a868;
      --text:#e8dcc8;--td:#a09070;--tm:#686050;
    }

    /* ── Per-theme Hero backgrounds ── */
    [data-theme="architect"] .hero{
      background:
        linear-gradient(to bottom,rgba(5,10,24,.82) 0%,rgba(5,10,24,.04) 30%,rgba(5,10,24,.04) 58%,rgba(5,10,24,.94) 100%),
        url('images/architect.png') center top / cover no-repeat,#050a18;
      border-color:rgba(85,170,255,.22)}
    [data-theme="architect"] .hero::before{
      background:linear-gradient(90deg,transparent,rgba(85,170,255,.7),rgba(85,119,238,.6),transparent)}
    [data-theme="architect"] .hero::after{
      background:linear-gradient(90deg,transparent,rgba(85,170,255,.05),transparent)}
    [data-theme="strategist"] .hero{
      background:
        linear-gradient(to bottom,rgba(240,240,234,.92) 0%,rgba(240,240,234,.1) 30%,rgba(240,240,234,.1) 58%,rgba(240,240,234,.96) 100%),
        url('images/strategist.png') center top / cover no-repeat,#f0f0ea;
      border-color:rgba(26,80,138,.2)}
    [data-theme="strategist"] .hero::before{
      background:linear-gradient(90deg,transparent,rgba(26,80,138,.4),rgba(90,58,138,.3),transparent)}
    [data-theme="strategist"] .hero::after{
      background:linear-gradient(90deg,transparent,rgba(26,80,138,.05),transparent)}
    [data-theme="strategist"] .hero-brand{color:var(--blue)}
    [data-theme="strategist"] .hero-name{color:var(--text)}
    [data-theme="strategist"] .hero-role{color:var(--td)}
    [data-theme="strategist"] .hero-metric{
      background:rgba(240,240,234,.68);border-color:rgba(26,80,138,.14)}
    [data-theme="strategist"] .hm-label{color:var(--td)}
    [data-theme="strategist"] .hm-value{color:var(--text)}
    [data-theme="strategist"] .hm-ai .hm-value{color:var(--green)}
    [data-theme="strategist"] .hm-note{color:var(--tm)}
    [data-theme="strategist"] .card:hover{box-shadow:0 8px 24px rgba(0,0,0,.1)}
    [data-theme="strategist"] .roi-box{background:linear-gradient(135deg,#f5f5f0 0%,rgba(90,58,138,.06) 100%);border-color:rgba(90,58,138,.18)}
    [data-theme="strategist"] .cal-day.today{background:linear-gradient(135deg,#fff,rgba(26,80,138,.04));border-color:rgba(26,80,138,.35)}
    [data-theme="investor"] .hero{
      background:
        linear-gradient(to bottom,rgba(9,9,8,.82) 0%,rgba(9,9,8,.04) 30%,rgba(9,9,8,.04) 58%,rgba(9,9,8,.94) 100%),
        url('images/investor.png') center top / cover no-repeat,#090908;
      border-color:rgba(200,144,24,.22)}
    [data-theme="investor"] .hero::before{
      background:linear-gradient(90deg,transparent,rgba(200,144,24,.6),rgba(224,184,56,.5),transparent)}
    [data-theme="investor"] .hero::after{
      background:linear-gradient(90deg,transparent,rgba(200,144,24,.05),transparent)}
    [data-theme="investor"] .hero-metric{border-color:rgba(200,144,24,.14)}
    [data-theme="investor"] .hm-value{color:var(--yellow)}
    [data-theme="investor"] .hm-ai .hm-value{color:var(--green)}
    [data-theme="investor"] .roi-box{border-color:rgba(200,144,24,.18)}

    /* ── Per-theme number/accent styling ── */
    [data-theme="architect"] .hm-value{text-shadow:0 0 22px rgba(85,170,255,.4)}
    [data-theme="architect"] .hm-ai .hm-value{text-shadow:0 0 18px rgba(58,200,138,.4)}
    [data-theme="architect"] .fin-val{text-shadow:0 0 14px rgba(85,170,255,.3)}
    [data-theme="architect"] .pj-metric{text-shadow:0 0 14px rgba(85,170,255,.3)}
    [data-theme="architect"] .focus-num{text-shadow:0 0 18px rgba(85,119,238,.5)}
    [data-theme="investor"] .fin-val{color:var(--yellow)}
    [data-theme="investor"] .pj-metric{color:var(--yellow)}
    [data-theme="investor"] .focus-num{color:var(--yellow)}
    [data-theme="strategist"] .fin-val{color:var(--text)}
    [data-theme="strategist"] .pj-metric{color:var(--text)}
    [data-theme="strategist"] .pj-name{color:var(--text)}
    [data-theme="strategist"] .focus-ttl{color:var(--text)}
    [data-theme="strategist"] .focus-num{color:var(--purple)}
    [data-theme="strategist"] .dec-title{color:var(--text)}
  </style>
</head>
<body>

<!-- ══ Hero ═════════════════════════════════════════════════ -->
<div class="hero fade-in">
  <!-- Top bar -->
  <div class="hero-top">
    <div>
      <div class="hero-brand">AI カンパニー 統合司令室</div>
      <div class="hero-top-status">
        <span class="status-pulse"></span>
        <span style="margin-left:2px">全システム稼働中 —</span>
        <span id="month-label" style="margin-left:4px"></span>
      </div>
    </div>
    <div class="hero-meta-wrap">
      <div class="hero-updated">最終更新: [[LAST_UPDATED]]</div>
      <div class="hero-auto">⟳ 毎朝 8:00 JST 自動更新</div>
      <a class="hero-edit" href="data.json" target="_blank">✏️ data.json を編集</a>
      <div class="th-wrap">
        <div class="th-label-text">スタイル切替</div>
        <div class="theme-switcher">
          <button class="th-btn" data-theme="commander" title="司令塔型">⚡</button>
          <button class="th-btn" data-theme="architect" title="建築家型">🏗️</button>
          <button class="th-btn" data-theme="strategist" title="戦略家型">♟️</button>
          <button class="th-btn" data-theme="investor" title="投資家型">💹</button>
        </div>
      </div>
    </div>
  </div>
  <!-- Bottom: name + metric chips -->
  <div class="hero-bottom">
    <div class="hero-name">岩嵜浩之</div>
    <div class="hero-role">AI カンパニー オーナー &amp; 代表</div>
    <div class="hero-metrics">
      <div class="hero-metric">
        <div class="hm-label">💰 手元資金</div>
        <div class="hm-value">¥[[CASH]]</div>
        <div class="hm-note">直近記録時点</div>
      </div>
      <div class="hero-metric">
        <div class="hm-label">📈 月次 MRR</div>
        <div class="hm-value">¥[[MRR]]</div>
        <div class="hm-note">目標 ¥398,000</div>
      </div>
      <div class="hero-metric">
        <div class="hm-label">🔒 月次固定費</div>
        <div class="hm-value">¥[[COST]]</div>
        <div class="hm-note">AIツール合計</div>
      </div>
      <div class="hero-metric hm-ai">
        <div class="hm-label">⚡ AI削減工数</div>
        <div class="hm-value">[[AI_HOURS]]h</div>
        <div class="hm-sub">≈ ¥[[ROI_NET]]/月 節約</div>
      </div>
    </div>
  </div>
</div>

<!-- ══ カレンダー ═══════════════════════════════════════════ -->
<div class="cal-strip fade-in">
  <div class="cal-strip-label">今週のスケジュール</div>
  <div class="cal-scroll">[[CALENDAR_HTML]]</div>
</div>

<!-- ══ 収益目標ダッシュボード ═══════════════════════════════ -->
<div class="section fade-in d1">
  <div class="sec-title">収益目標 <span class="sec-cat-badge badge-pro" style="margin-left:8px">月次進捗</span></div>
  <div class="fin-grid">
    <div class="card fin-card">
      <div class="fin-label">🧑 月収・報酬</div>
      <div class="fin-val">¥[[SALARY]]</div>
      <div class="fin-target">目標 ¥[[SALARY_TARGET]]/月</div>
      <div class="fin-bar"><div class="fin-fill" style="width:[[SALARY_PCT]]%"></div></div>
    </div>
    <div class="card fin-card">
      <div class="fin-label">🛍️ EC（Daiwa）</div>
      <div class="fin-val">¥[[EC_MRR]]</div>
      <div class="fin-target">目標 ¥[[EC_MRR_TARGET]]/月</div>
      <div class="fin-bar"><div class="fin-fill blue" style="width:[[EC_PCT]]%"></div></div>
    </div>
    <div class="card fin-card">
      <div class="fin-label">🔧 Amazon Toolkit</div>
      <div class="fin-val">¥[[TOOLKIT_MRR]]</div>
      <div class="fin-target">目標 ¥[[TOOLKIT_MRR_TARGET]]/月</div>
      <div class="fin-bar"><div class="fin-fill" style="width:[[TOOLKIT_PCT]]%"></div></div>
    </div>
    <div class="card fin-card">
      <div class="fin-label">🤖 AIコンサル</div>
      <div class="fin-val">¥[[CONSULT_MRR]]</div>
      <div class="fin-target">目標 ¥[[CONSULT_MRR_TARGET]]/月</div>
      <div class="fin-bar"><div class="fin-fill green" style="width:[[CONSULT_PCT]]%"></div></div>
    </div>
    <div class="card fin-card">
      <div class="fin-label">🐻 BearGo</div>
      <div class="fin-val">¥[[BEARGO_MRR]]</div>
      <div class="fin-target">目標 ¥[[BEARGO_MRR_TARGET]]/月</div>
      <div class="fin-bar"><div class="fin-fill blue" style="width:[[BEARGO_PCT]]%"></div></div>
    </div>
  </div>
</div>

<!-- ══ プロジェクト状況 ════════════════════════════════════ -->
<div class="section fade-in d2">
  <div class="sec-title">
    プロジェクト状況
    <span class="sec-cat-badge badge-pro" style="margin-left:8px">ビジネス</span>
    <span class="sec-cat-badge badge-personal" style="margin-left:4px">パーソナル</span>
  </div>
  <div class="project-grid">

    <!-- EC -->
    <div class="card project-card pro-card">
      <div class="cat-tag tag-pro">ビジネス</div>
      <div style="position:relative">
        <div class="emoji-wrap" data-proj="ec" onclick="togglePicker(this)">
          <span class="emoji-face">🛍️</span><span class="emoji-hint">変更</span>
        </div>
        <div class="emoji-picker" data-for="ec">
          <div class="ep-opt" onclick="pickEmoji(this,'ec')">🛍️</div><div class="ep-opt" onclick="pickEmoji(this,'ec')">📦</div>
          <div class="ep-opt" onclick="pickEmoji(this,'ec')">🏪</div><div class="ep-opt" onclick="pickEmoji(this,'ec')">💰</div>
          <div class="ep-opt" onclick="pickEmoji(this,'ec')">🛒</div><div class="ep-opt" onclick="pickEmoji(this,'ec')">🌸</div>
          <div class="ep-opt" onclick="pickEmoji(this,'ec')">💎</div><div class="ep-opt" onclick="pickEmoji(this,'ec')">✨</div>
        </div>
      </div>
      <div class="pj-row">
        <div><div class="pj-name">EC（Daiwa Felicity）</div><div class="pj-sub">USJ-815 / Amazon → Shopify予定</div></div>
        <span class="badge b-active"><span class="bdot"></span>稼働中</span>
      </div>
      <div class="pj-metric">¥[[EC_MRR]]</div>
      <div class="pj-metric-label">月次 MRR</div>
      <div class="prog-bar"><div class="prog-fill fill-teal" style="width:0%"></div></div>
      [[EC_NEXTS_HTML]]
    </div>

    <!-- Toolkit -->
    <div class="card project-card pro-card">
      <div class="cat-tag tag-pro">ビジネス</div>
      <div style="position:relative">
        <div class="emoji-wrap" data-proj="toolkit" onclick="togglePicker(this)">
          <span class="emoji-face">🔧</span><span class="emoji-hint">変更</span>
        </div>
        <div class="emoji-picker" data-for="toolkit">
          <div class="ep-opt" onclick="pickEmoji(this,'toolkit')">🔧</div><div class="ep-opt" onclick="pickEmoji(this,'toolkit')">⚙️</div>
          <div class="ep-opt" onclick="pickEmoji(this,'toolkit')">🛠️</div><div class="ep-opt" onclick="pickEmoji(this,'toolkit')">📊</div>
          <div class="ep-opt" onclick="pickEmoji(this,'toolkit')">📈</div><div class="ep-opt" onclick="pickEmoji(this,'toolkit')">⚡</div>
          <div class="ep-opt" onclick="pickEmoji(this,'toolkit')">🔬</div><div class="ep-opt" onclick="pickEmoji(this,'toolkit')">💡</div>
        </div>
      </div>
      <div class="pj-row">
        <div><div class="pj-name">Amazon Toolkit</div><div class="pj-sub">B2B SaaS / Cloudflare Pages</div></div>
        <span class="badge b-build"><span class="bdot"></span>開発中</span>
      </div>
      <div class="pj-metric">¥[[TOOLKIT_MRR]]</div>
      <div class="pj-metric-label">MRR / 目標 ¥98,000〜¥498,000</div>
      <div class="prog-bar"><div class="prog-fill fill-yellow" style="width:0%"></div></div>
      [[TOOLKIT_NEXTS_HTML]]
    </div>

    <!-- Consult -->
    <div class="card project-card pro-card">
      <div class="cat-tag tag-pro">ビジネス</div>
      <div style="position:relative">
        <div class="emoji-wrap" data-proj="consult" onclick="togglePicker(this)">
          <span class="emoji-face">🤖</span><span class="emoji-hint">変更</span>
        </div>
        <div class="emoji-picker" data-for="consult">
          <div class="ep-opt" onclick="pickEmoji(this,'consult')">🤖</div><div class="ep-opt" onclick="pickEmoji(this,'consult')">💡</div>
          <div class="ep-opt" onclick="pickEmoji(this,'consult')">🎯</div><div class="ep-opt" onclick="pickEmoji(this,'consult')">🧠</div>
          <div class="ep-opt" onclick="pickEmoji(this,'consult')">✨</div><div class="ep-opt" onclick="pickEmoji(this,'consult')">🚀</div>
          <div class="ep-opt" onclick="pickEmoji(this,'consult')">💼</div><div class="ep-opt" onclick="pickEmoji(this,'consult')">🌟</div>
        </div>
      </div>
      <div class="pj-row">
        <div><div class="pj-name">AI自動化コンサル</div><div class="pj-sub">AIX × 岩嵜 / YuYA差別化戦略</div></div>
        <span class="badge b-ready"><span class="bdot"></span>営業準備中</span>
      </div>
      <div class="pj-metric">[[CONSULT_CLIENTS]]社</div>
      <div class="pj-metric-label">成約数 / 目標 月額¥300,000+</div>
      <div class="prog-bar"><div class="prog-fill fill-purple" style="width:0%"></div></div>
      [[CONSULT_NEXTS_HTML]]
    </div>

    <!-- BearGo -->
    <div class="card project-card pro-card">
      <div class="cat-tag tag-pro">ビジネス</div>
      <div style="position:relative">
        <div class="emoji-wrap" data-proj="beargo" onclick="togglePicker(this)">
          <span class="emoji-face">🐻</span><span class="emoji-hint">変更</span>
        </div>
        <div class="emoji-picker" data-for="beargo">
          <div class="ep-opt" onclick="pickEmoji(this,'beargo')">🐻</div><div class="ep-opt" onclick="pickEmoji(this,'beargo')">📚</div>
          <div class="ep-opt" onclick="pickEmoji(this,'beargo')">🌟</div><div class="ep-opt" onclick="pickEmoji(this,'beargo')">🎨</div>
          <div class="ep-opt" onclick="pickEmoji(this,'beargo')">🌈</div><div class="ep-opt" onclick="pickEmoji(this,'beargo')">🧸</div>
          <div class="ep-opt" onclick="pickEmoji(this,'beargo')">🎪</div><div class="ep-opt" onclick="pickEmoji(this,'beargo')">🌙</div>
        </div>
      </div>
      <div class="pj-row">
        <div><div class="pj-name">BearGo</div><div class="pj-sub">AI絵本 / 30〜40代ママ向け</div></div>
        <span class="badge b-build"><span class="bdot"></span>テスター稼働中</span>
      </div>
      <div class="pj-metric">[[BEARGO_BOOKS]]冊</div>
      <div class="pj-metric-label">生成済み / 目標 246冊</div>
      <div class="prog-bar"><div class="prog-fill fill-teal" id="bg-prog"></div></div>
      [[BEARGO_NEXTS_HTML]]
    </div>

    <!-- Minecraft -->
    <div class="card project-card personal-card">
      <div class="cat-tag tag-personal">パーソナル</div>
      <div style="position:relative">
        <div class="emoji-wrap" data-proj="minecraft" onclick="togglePicker(this)">
          <span class="emoji-face">🎮</span><span class="emoji-hint">変更</span>
        </div>
        <div class="emoji-picker" data-for="minecraft">
          <div class="ep-opt" onclick="pickEmoji(this,'minecraft')">🎮</div><div class="ep-opt" onclick="pickEmoji(this,'minecraft')">🧱</div>
          <div class="ep-opt" onclick="pickEmoji(this,'minecraft')">⚔️</div><div class="ep-opt" onclick="pickEmoji(this,'minecraft')">🏆</div>
          <div class="ep-opt" onclick="pickEmoji(this,'minecraft')">🌍</div><div class="ep-opt" onclick="pickEmoji(this,'minecraft')">💎</div>
          <div class="ep-opt" onclick="pickEmoji(this,'minecraft')">🦁</div><div class="ep-opt" onclick="pickEmoji(this,'minecraft')">🎯</div>
        </div>
      </div>
      <div class="pj-row">
        <div><div class="pj-name">Minecraft英語ゲーム</div><div class="pj-sub">4歳息子向け / 無料公開</div></div>
        <span class="badge b-active"><span class="bdot"></span>稼働中</span>
      </div>
      <div class="pj-metric">−</div>
      <div class="pj-metric-label">無料公開中（収益化未定）</div>
      <div class="prog-bar"><div class="prog-fill fill-blue" style="width:100%"></div></div>
      [[MINECRAFT_NEXTS_HTML]]
    </div>

    <!-- DiaryHolic -->
    <div class="card project-card personal-card">
      <div class="cat-tag tag-personal">パーソナル</div>
      <div style="position:relative">
        <div class="emoji-wrap" data-proj="diary" onclick="togglePicker(this)">
          <span class="emoji-face">📔</span><span class="emoji-hint">変更</span>
        </div>
        <div class="emoji-picker" data-for="diary">
          <div class="ep-opt" onclick="pickEmoji(this,'diary')">📔</div><div class="ep-opt" onclick="pickEmoji(this,'diary')">✏️</div>
          <div class="ep-opt" onclick="pickEmoji(this,'diary')">💭</div><div class="ep-opt" onclick="pickEmoji(this,'diary')">🌸</div>
          <div class="ep-opt" onclick="pickEmoji(this,'diary')">🎨</div><div class="ep-opt" onclick="pickEmoji(this,'diary')">📖</div>
          <div class="ep-opt" onclick="pickEmoji(this,'diary')">💫</div><div class="ep-opt" onclick="pickEmoji(this,'diary')">🌙</div>
        </div>
      </div>
      <div class="pj-row">
        <div><div class="pj-name">DiaryHolic</div><div class="pj-sub">日記アプリ / diaryholic.pages.dev</div></div>
        <span class="badge b-active"><span class="bdot"></span>稼働中</span>
      </div>
      <div class="pj-metric">−</div>
      <div class="pj-metric-label">無料公開中（収益化未定）</div>
      <div class="prog-bar"><div class="prog-fill fill-blue" style="width:100%"></div></div>
      [[DIARY_NEXTS_HTML]]
    </div>

  </div>
</div>

<!-- ══ AI自動化マトリクス ════════════════════════════════== -->
<div class="section fade-in d3">
  <div class="sec-title">AI自動化マトリクス</div>
  <div class="auto-grid">
    <div class="card auto-panel">
      <div class="auto-title"><span class="dot-pulse"></span>稼働中の自動化（8個）— 合計 [[AI_HOURS]]h/月 削減</div>
      <div class="auto-row"><div><div class="auto-name">CS自動下書き生成</div><div class="auto-tech">Google Apps Script + Gmail</div></div><div class="auto-save">-8h/月</div></div>
      <div class="auto-row"><div><div class="auto-name">Instagram自動投稿（Daiwa）</div><div class="auto-tech">Python + GitHub Actions</div></div><div class="auto-save">-12h/月</div></div>
      <div class="auto-row"><div><div class="auto-name">ブログ自動投稿（Daiwa）</div><div class="auto-tech">GitHub Actions / 月・木 9:00</div></div><div class="auto-save">-8h/月</div></div>
      <div class="auto-row"><div><div class="auto-name">SEOキーワード分析</div><div class="auto-tech">Python / Level 1.5稼働中</div></div><div class="auto-save">-16h/月</div></div>
      <div class="auto-row"><div><div class="auto-name">BearGo絵本夜間自動生成</div><div class="auto-tech">Python + gpt-image-1 / nightly.bat</div></div><div class="auto-save">-80h/月</div></div>
      <div class="auto-row"><div><div class="auto-name">Amazon広告最適化ツール</div><div class="auto-tech">HTML/JS / Cloudflare Pages</div></div><div class="auto-save">-12h/月</div></div>
      <div class="auto-row"><div><div class="auto-name">Amazon画像最適化ツール</div><div class="auto-tech">Node.js / localhost:3333</div></div><div class="auto-save">-4h/月</div></div>
      <div class="auto-row"><div><div class="auto-name">Amazon SEOキーワードツール</div><div class="auto-tech">Python + HTML / ローカル</div></div><div class="auto-save">-4h/月</div></div>
    </div>
    <div class="card auto-panel">
      <div class="auto-title"><span class="dot-idle"></span>実装予定（3個）</div>
      <div class="auto-row"><div><div class="auto-name">AI自動化コンサル Cockpit</div><div class="auto-tech">会社情報→AI施策提案ダッシュボード</div></div><span class="wip-badge">設計中</span></div>
      <div class="auto-row"><div><div class="auto-name">Progrit添削自動化</div><div class="auto-tech">Playwright + Whisper + Claude</div></div><span class="wip-badge">設計中</span></div>
      <div class="auto-row"><div><div class="auto-name">Amazon SEO Level 3</div><div class="auto-tech">LINE通知連携</div></div><span class="wip-badge">次スプリント</span></div>
      <div class="roi-box">
        <div class="roi-box-label">もし全部人間でやったら…</div>
        <div class="roi-box-val">¥[[ROI_GROSS]]/月</div>
        <div class="roi-box-sub">= [[AI_HOURS]]h × ¥2,000/h</div>
        <div class="roi-box-net">実質 ¥[[ROI_NET]]/月 の節約</div>
      </div>
    </div>
  </div>
</div>

<!-- ══ フォーカス + 意思決定 ════════════════════════════════ -->
<div class="two-col fade-in d4">
  <div class="section">
    <div class="sec-title">今月のフォーカス（Top 3）</div>
    <div class="card focus-item">
      <div class="focus-num">1</div>
      <div class="focus-body">
        <div class="focus-ttl">[[FOCUS_1_TITLE]]</div>
        <div class="focus-desc">[[FOCUS_1_DESC]]</div>
      </div>
      <div class="focus-dl">[[FOCUS_1_DL]]</div>
    </div>
    <div class="card focus-item">
      <div class="focus-num">2</div>
      <div class="focus-body">
        <div class="focus-ttl">[[FOCUS_2_TITLE]]</div>
        <div class="focus-desc">[[FOCUS_2_DESC]]</div>
      </div>
      <div class="focus-dl">[[FOCUS_2_DL]]</div>
    </div>
    <div class="card focus-item">
      <div class="focus-num">3</div>
      <div class="focus-body">
        <div class="focus-ttl">[[FOCUS_3_TITLE]]</div>
        <div class="focus-desc">[[FOCUS_3_DESC]]</div>
      </div>
      <div class="focus-dl">[[FOCUS_3_DL]]</div>
    </div>
  </div>
  <div class="section">
    <div class="sec-title">直近の意思決定</div>
    <div class="card dec-item">
      <div class="dec-date">[[DEC_1_DATE]]</div>
      <div class="dec-title">[[DEC_1_TITLE]]</div>
      <div class="dec-reason">[[DEC_1_REASON]]</div>
    </div>
    <div class="card dec-item">
      <div class="dec-date">[[DEC_2_DATE]]</div>
      <div class="dec-title">[[DEC_2_TITLE]]</div>
      <div class="dec-reason">[[DEC_2_REASON]]</div>
    </div>
    <div class="card dec-item">
      <div class="dec-date">[[DEC_3_DATE]]</div>
      <div class="dec-title">[[DEC_3_TITLE]]</div>
      <div class="dec-reason">[[DEC_3_REASON]]</div>
    </div>
  </div>
</div>

<!-- ══ 変更履歴 ════════════════════════════════════════════ -->
<div class="section fade-in d5">
  <div class="sec-title">変更履歴</div>
  <div class="hist-list">[[HISTORY_HTML]]</div>
</div>

<div class="footer fade-in d5">
  K-Cockpit — 岩嵜 AI カンパニー 統合司令室 — 毎朝 8:00 JST 自動更新
</div>

<script>
  // Theme switcher
  (function(){
    var saved = localStorage.getItem('cp_theme') || 'commander';
    document.documentElement.setAttribute('data-theme', saved);
    document.querySelectorAll('.th-btn').forEach(function(btn){
      if(btn.dataset.theme === saved) btn.classList.add('active');
      btn.addEventListener('click', function(){
        var t = btn.dataset.theme;
        document.documentElement.setAttribute('data-theme', t);
        localStorage.setItem('cp_theme', t);
        document.querySelectorAll('.th-btn').forEach(function(b){
          b.classList.toggle('active', b === btn);
        });
      });
    });
  })();

  // 月ラベル
  const now = new Date();
  document.getElementById('month-label').textContent = now.getFullYear()+'年'+(now.getMonth()+1)+'月';

  // BearGo進捗バー
  const bgBooks = parseInt('[[BEARGO_BOOKS]]'.replace(/[^0-9]/g,''),10) || 0;
  const bgEl = document.getElementById('bg-prog');
  if(bgEl) bgEl.style.width = Math.min(100, Math.round(bgBooks/246*100))+'%';

  // Emoji picker
  let openPicker = null;
  function togglePicker(wrap){
    const proj=wrap.dataset.proj;
    const picker=document.querySelector('.emoji-picker[data-for="'+proj+'"]');
    if(!picker) return;
    if(picker.classList.contains('open')){picker.classList.remove('open');openPicker=null;return}
    if(openPicker) openPicker.classList.remove('open');
    picker.classList.add('open'); openPicker=picker;
  }
  function pickEmoji(opt,proj){
    const emoji=opt.textContent;
    const wrap=document.querySelector('.emoji-wrap[data-proj="'+proj+'"]');
    const face=wrap.querySelector('.emoji-face');
    const picker=document.querySelector('.emoji-picker[data-for="'+proj+'"]');
    face.textContent=emoji;
    face.classList.add('emoji-bounce');
    setTimeout(()=>face.classList.remove('emoji-bounce'),300);
    picker.classList.remove('open'); openPicker=null;
    localStorage.setItem('cp_emoji_'+proj,emoji);
  }
  ['ec','toolkit','consult','beargo','minecraft','diary'].forEach(p=>{
    const s=localStorage.getItem('cp_emoji_'+p);
    if(s){const f=document.querySelector('.emoji-wrap[data-proj="'+p+'"] .emoji-face');if(f)f.textContent=s;}
  });
  document.addEventListener('click',e=>{
    if(openPicker && !e.target.closest('.emoji-wrap') && !e.target.closest('.emoji-picker')){
      openPicker.classList.remove('open'); openPicker=null;
    }
  });
</script>
</body>
</html>"""

# ── 8. プレースホルダーを置換 ─────────────────────────────────
result = TEMPLATE
for key, value in data.items():
    if isinstance(value, str):
        result = result.replace(f"[[{key.upper()}]]", value)

# ── 9. index.html を出力 ──────────────────────────────────────
with open("index.html", "w", encoding="utf-8") as f:
    f.write(result)

print(f"[OK] K-Cockpit v2 generated  last_updated: {data['last_updated']}")
