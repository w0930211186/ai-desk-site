#!/usr/bin/env python3
"""
ai-desk · regen-build-artifacts
================================

掃 posts/ 下全部 daily / weekly / news HTML，重新產：
  1. sitemap.xml   — 全部 URL
  2. rss.xml       — top 20 items
  3. index.html    — EDITION N°XX, 日期, X PUBLISHED, LATEST EDITIONS 卡片區

跑法：
    python3 scripts/regen-build-artifacts.py

冪等：可重複跑，輸出穩定。
接到 ai-desk-publish skill 末尾，每次 publish 完自動 regen + commit + push。
"""
import re
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta
from html import escape

ROOT = Path(__file__).resolve().parent.parent
POSTS = ROOT / "posts"
SITEMAP = ROOT / "sitemap.xml"
RSS = ROOT / "rss.xml"
INDEX = ROOT / "index.html"

SITE = "https://ai-desk-tw.netlify.app"
CST = timezone(timedelta(hours=8))

# Match files like 2026-04-27-daily.html / 2026-04-24-ai-daily.html / 2026-05-03-weekly.html
POST_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})-(.+)\.html$")
EXCLUDE = {"index.html", "_template.html", "2026-04-24-ai-desk-opening.html"}  # opening v4 起 archived


def parse_post(p: Path) -> dict | None:
    """從一篇 HTML 抽：date / slug / category / title / desc / og_title / edition"""
    m = POST_RE.match(p.name)
    if not m:
        return None
    yyyy, mm, dd, rest = m.groups()
    date = datetime(int(yyyy), int(mm), int(dd), 7, 0, tzinfo=CST)

    text = p.read_text(encoding="utf-8")

    title = _first(re.search(r"<title>([^<]+)</title>", text))
    desc = _first(re.search(r'<meta\s+name=["\']description["\']\s+content=["\']([^"\']+)["\']', text))
    og_title = _first(re.search(r'<meta\s+property=["\']og:title["\']\s+content=["\']([^"\']+)["\']', text))
    edition_m = re.search(r"Edition\s*N°(\d+)", text) or re.search(r"N°(\d+)", text)
    edition = int(edition_m.group(1)) if edition_m else 0

    # 推 category
    if "ai-daily" in rest or rest == "daily":
        category = "daily"
        cat_label = "Daily · 大事"
    elif "weekly" in rest:
        category = "weekly"
        cat_label = "Weekly · 週回顧"
    elif "news" in rest:
        category = "news"
        cat_label = "News · 新聞"
    elif "opening" in rest:
        category = "meta"
        cat_label = "Meta · 站務"
    else:
        category = "daily"
        cat_label = "Daily · 大事"

    return {
        "filename": p.name,
        "slug": p.stem,  # 2026-04-27-daily
        "date": date,
        "title": title or p.stem,
        "og_title": og_title or title or p.stem,
        "desc": desc or "",
        "edition": edition,
        "category": category,
        "cat_label": cat_label,
        "url": f"{SITE}/posts/{p.name}",
        "url_clean": f"{SITE}/posts/{p.stem}",
    }


def _first(m):
    return m.group(1).strip() if m else None


def collect_posts() -> list[dict]:
    posts = []
    for p in POSTS.glob("*.html"):
        if p.name in EXCLUDE:
            continue
        info = parse_post(p)
        if info:
            posts.append(info)
    posts.sort(key=lambda x: (x["date"], x["edition"]), reverse=True)
    return posts


# ============================================================
# 1. sitemap.xml
# ============================================================

def gen_sitemap(posts: list[dict]) -> str:
    today = datetime.now(CST).strftime("%Y-%m-%d")
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']

    static_urls = [
        ("/", today, "daily", "1.0"),
        ("/posts/", today, "daily", "0.9"),
        ("/latest", today, "daily", "0.7"),
    ]
    for path, lastmod, freq, prio in static_urls:
        lines.append(f"  <url>")
        lines.append(f"    <loc>{SITE}{path}</loc>")
        lines.append(f"    <lastmod>{lastmod}</lastmod>")
        lines.append(f"    <changefreq>{freq}</changefreq>")
        lines.append(f"    <priority>{prio}</priority>")
        lines.append(f"  </url>")

    for post in posts:
        lines.append(f"  <url>")
        lines.append(f"    <loc>{post['url']}</loc>")
        lines.append(f"    <lastmod>{post['date'].strftime('%Y-%m-%d')}</lastmod>")
        lines.append(f"    <changefreq>monthly</changefreq>")
        lines.append(f"    <priority>0.8</priority>")
        lines.append(f"  </url>")

    lines.append("</urlset>")
    return "\n".join(lines) + "\n"


# ============================================================
# 2. rss.xml
# ============================================================

def gen_rss(posts: list[dict]) -> str:
    now = datetime.now(timezone.utc)
    last_build = now.strftime("%a, %d %b %Y %H:%M:%S +0000")

    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">',
           '  <channel>',
           f'    <title>AI DESK</title>',
           f'    <link>{SITE}/</link>',
           f'    <description>獨立 AI 編輯台 · 每天 07:00 CST · 1 分鐘看完全球 AI 大事 · 每條附源</description>',
           f'    <language>zh-Hant</language>',
           f'    <lastBuildDate>{last_build}</lastBuildDate>',
           f'    <atom:link href="{SITE}/rss.xml" rel="self" type="application/rss+xml" />']

    for post in posts[:20]:
        pub = post["date"].strftime("%a, %d %b %Y %H:%M:%S +0800")
        title = escape(post["og_title"])
        link = post["url"]
        desc = escape(post["desc"])
        out += [
            '    <item>',
            f'      <title>{title}</title>',
            f'      <link>{link}</link>',
            f'      <guid isPermaLink="true">{link}</guid>',
            f'      <pubDate>{pub}</pubDate>',
            f'      <description>{desc}</description>',
            '    </item>',
        ]

    out += ['  </channel>', '</rss>']
    return "\n".join(out) + "\n"


# ============================================================
# 3. index.html — 動態替換 edition / 計數器 / 卡片區
# ============================================================

def gen_index_card(post: dict, slot_class: str) -> str:
    """產一張 LATEST EDITIONS 卡片（真實文章版）"""
    return (
        f'    <a href="posts/{post["filename"]}" class="journal-card {slot_class} reveal" data-tags="{post["category"]}">\n'
        f'      <div class="card-meta"><span>N°{post["edition"]:02d}</span><span>{post["date"].strftime("%Y · %m · %d")}</span></div>\n'
        f'      <h3>{escape(post["og_title"])}</h3>\n'
        f'      <p>{escape(post["desc"])}</p>\n'
        f'      <div class="card-foot"><span>{post["cat_label"]}</span><span class="arrow">→</span></div>\n'
        f'    </a>\n'
    )


def gen_index_ghost_card(slot_class: str, edition_num: int, category: str, label: str, title_html: str, body: str) -> str:
    """產一張 ghost 卡片（COMING placeholder，當實際文章不夠時）"""
    return (
        f'    <div class="journal-card ghost {slot_class} reveal" data-tags="{category}">\n'
        f'      <div class="card-meta"><span>N°{edition_num:02d}</span><span>Coming</span></div>\n'
        f'      <h3>{title_html}</h3>\n'
        f'      <p>{body}</p>\n'
        f'      <div class="card-foot"><span>{label}</span><span class="arrow">→</span></div>\n'
        f'    </div>\n'
    )


def update_index(posts: list[dict]) -> bool:
    text = INDEX.read_text(encoding="utf-8")
    orig = text

    latest = posts[0] if posts else None
    count = len(posts)
    max_edition = max((p["edition"] for p in posts), default=0)

    # ---- (a) hero-caption .right: 「2026 · 04 · 24 / FRI」+「EDITION N°01」----
    if latest:
        date_str = latest["date"].strftime("%Y · %m · %d / %a").upper()
        # 把整段 .right 內容換掉
        text = re.sub(
            r'(<div class="right">)\s*[^<]+<br>\s*EDITION\s*N°\d+\s*(</div>)',
            rf'\1\n      {date_str}<br>\n      EDITION N°{max_edition:02d}\n    \2',
            text, count=1
        )

    # ---- (b) section-label「6 slots · 1 published」----
    text = re.sub(
        r'<span>(\d+\s*slots?\s*·\s*)\d+\s*published</span>',
        rf'<span>{max(count, 6)} slots · {count} published</span>',
        text, count=1
    )

    # ---- (c) FEED-INJECTION 區塊：填真實文章 + 缺位用 ghost 補 ----
    slot_classes = ["c1", "c2", "c3", "c4", "c5", "c6"]
    cards_html = ""
    # 真實文章先填
    for i, post in enumerate(posts[:6]):
        cards_html += gen_index_card(post, slot_classes[i])
    # 不夠 6 張用 ghost 補
    ghosts = [
        ("daily", "Daily · 大事", "AI 大事<br>下一篇 07:00 上線", "每天 07:00 CST · 三到五條過去 24 小時真正要命的 AI 大事 每條附原始網址 看完走人。"),
        ("news", "News · 新聞", "AI 新聞精選<br>這週值得深讀的一條", "每週二 · 五 07:00 從七天的大事裡挑一件真正有後座力的 把前因後果拆到你懂為止。"),
        ("weekly", "Weekly · 週回顧", "一週回顧<br>七天 AI 大事一口氣掃", "每週日 09:00 CST 把整週的 AI 大事按時間線排好 重要度標註 錯過的也能一次補回來。"),
        ("meta", "Meta · 站務", "Meta · 站務<br>編輯台自己的事", "季度一次 講這個編輯台怎麼運作 供稿管線 AI 怎麼跑 人工怎麼守門 全透明 給讀者看後台。"),
        ("weekly", "Weekly · 長文", "週末長文<br>一件值得想兩天的事", "不定期 · 週末上線 一個 AI 大命題 拆開來用三千字說清楚 不趕 KPI 只寫給會讀完的人。"),
    ]
    fill = len(posts)
    while fill < 6:
        ghost_idx = (fill - len(posts)) % len(ghosts)
        cat, label, htitle, body = ghosts[ghost_idx]
        cards_html += gen_index_ghost_card(slot_classes[fill], max_edition + (fill - len(posts)) + 1, cat, label, htitle, body)
        fill += 1

    text = re.sub(
        r'(<!-- FEED-INJECTION-START -->)[\s\S]*?(<!-- FEED-INJECTION-END -->)',
        lambda m: f'{m.group(1)}\n{cards_html.rstrip()}\n    {m.group(2)}',
        text, count=1
    )

    if text != orig:
        INDEX.write_text(text, encoding="utf-8")
        return True
    return False


# ============================================================
# main
# ============================================================

def main():
    posts = collect_posts()
    print(f"=== Found {len(posts)} posts ===")
    for p in posts:
        print(f"  N°{p['edition']:02d}  {p['date'].strftime('%Y-%m-%d')}  {p['filename']}  ({p['category']})")

    SITEMAP.write_text(gen_sitemap(posts), encoding="utf-8")
    print(f"✓ sitemap.xml — {len(posts) + 3} URLs")

    RSS.write_text(gen_rss(posts), encoding="utf-8")
    print(f"✓ rss.xml — {min(len(posts), 20)} items")

    if update_index(posts):
        print(f"✓ index.html — edition / counter / cards 已更新")
    else:
        print(f"  index.html — 無變更")


if __name__ == "__main__":
    main()
