import requests, smtplib, os
from datetime import date, timezone, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import xml.etree.ElementTree as ET

# ── 用 HackerNews RSS 抓取新闻（完全免费，无需API Key）──
feed_url = "https://hnrss.org/frontpage?count=15"
resp = requests.get(feed_url, timeout=15)
root = ET.fromstring(resp.content)
items = root.findall("./channel/item")

cst = timezone(timedelta(hours=8))
today = date.today().strftime("%Y年%m月%d日")

cards = ""
for item in items[:15]:
    title = item.findtext("title") or ""
    link  = item.findtext("link")  or "#"
    desc  = item.findtext("description") or ""
    # 去掉desc里的HTML标签
    import re
    desc = re.sub(r"<[^>]+>", "", desc).strip()[:120]
    cards += f"""
    <div class="card">
      <a href="{link}" target="_blank"><h2>{title}</h2></a>
      <p>{desc}</p>
    </div>"""

html = f"""<!DOCTYPE html>
<html lang="zh"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>每日科技新闻 · {today}</title>
<style>
  body{{font-family:system-ui,sans-serif;max-width:820px;margin:0 auto;padding:20px 16px;background:#0f1117;color:#e0e0e0}}
  h1{{font-size:22px;border-left:4px solid #4361ee;padding-left:12px;margin-bottom:24px}}
  .card{{background:#1a1d27;border-radius:10px;padding:18px 20px;margin:12px 0;border:1px solid #2a2d3a}}
  .card:hover{{border-color:#4361ee}}
  .card h2{{font-size:15px;margin:0 0 8px;line-height:1.5}}
  .card a{{text-decoration:none;color:#7eb3ff}}
  .card a:hover{{color:#a8ccff}}
  .card p{{color:#888;font-size:13px;margin:0;line-height:1.6}}
  footer{{text-align:center;color:#444;margin-top:32px;font-size:12px}}
</style></head>
<body>
  <h1>每日科技新闻 · {today}</h1>
  {cards}
  <footer>自动生成 · 由 GitHub Actions 驱动 · 数据来自 Hacker News</footer>
</body></html>"""

# ── 写入网页文件 ──
os.makedirs("docs", exist_ok=True)
with open("docs/index.html", "w", encoding="utf-8") as f:
    f.write(html)
print("✅ 网页已生成")

# ── 发送邮件 ──
SMTP_USER = os.environ["SMTP_USER"]
SMTP_PASS = os.environ["SMTP_PASS"]
TO_EMAIL  = os.environ["TO_EMAIL"]

msg = MIMEMultipart("alternative")
msg["Subject"] = f"📰 每日科技新闻 {today}"
msg["From"]    = SMTP_USER
msg["To"]      = TO_EMAIL
msg.attach(MIMEText(html, "html"))

with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
    s.login(SMTP_USER, SMTP_PASS)
    s.sendmail(SMTP_USER, TO_EMAIL, msg.as_string())
print("✅ 邮件已发送")
