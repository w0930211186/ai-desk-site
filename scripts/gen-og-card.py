#!/usr/bin/env python3
"""
ai-desk · gen-og-card
======================

為每篇文章產 1200×630 OG card（X / LinkedIn / Threads / FB / Pocket / Slack 通用）。

跑法：
  # 為單篇產
  python3 scripts/gen-og-card.py posts/2026-04-27-daily.html

  # 掃 posts/ 全部產（推薦）
  python3 scripts/gen-og-card.py --all

輸出：
  assets/og/<slug>-og.png       — 每篇專屬
  assets/og-cover.png            — fallback（用最新一篇產出，覆寫舊的壞圖）

設計：
  · 黑底 + 白字 mono brutalist
  · 左上 lockup：◆ AI DESK
  · 中間：標題（最多 3 行，自動 wrap）
  · 左下：Edition + 日期
  · 右下：ai-desk-tw.netlify.app/<slug>
  · 右上：「DAILY」/「WEEKLY」/「NEWS」分類 chip
"""
import argparse
import re
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
POSTS = ROOT / "posts"
ASSETS = ROOT / "assets"
OG_DIR = ASSETS / "og"
OG_DIR.mkdir(parents=True, exist_ok=True)
DEFAULT_OG = ASSETS / "og-cover.png"

FONTS_DIR = ROOT / "skills" / "ai-desk-ig-story" / "fonts"
F_DISPLAY = FONTS_DIR / "InterTight-VF.ttf"
F_CJK_BLACK = FONTS_DIR / "NotoSansCJKtc-Black.otf"
F_CJK_REGULAR = FONTS_DIR / "NotoSansCJKtc-Regular.otf"

W, H = 1200, 630
BG = (0, 0, 0)
FG = (255, 255, 255)
MUTE = (138, 138, 138)
MUTE_2 = (90, 90, 90)
LINE = (255, 255, 255, 36)


def load_font(path: Path, size: int):
    return ImageFont.truetype(str(path), size)


def parse_post(p: Path) -> dict | None:
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})-(.+)\.html$", p.name)
    if not m:
        return None
    yyyy, mm, dd, rest = m.groups()
    text = p.read_text(encoding="utf-8")
    og_title = _first(re.search(r'<meta\s+property=["\']og:title["\']\s+content=["\']([^"\']+)["\']', text))
    title = og_title or _first(re.search(r"<title>([^<|]+)", text)) or p.stem
    edition_m = re.search(r"Edition\s*N°(\d+)", text) or re.search(r"N°(\d+)", text)
    edition = int(edition_m.group(1)) if edition_m else 0

    if "weekly" in rest:
        category = "WEEKLY · 週回顧"
    elif "news" in rest:
        category = "NEWS · 新聞"
    elif "opening" in rest:
        category = "META · 站務"
    else:
        category = "DAILY · AI 大事"

    return {
        "filename": p.name,
        "slug": p.stem,
        "date": f"{yyyy} · {mm} · {dd}",
        "year": yyyy, "mm": mm, "dd": dd,
        "title": title.strip(),
        "edition": edition,
        "category": category,
        "url_path": f"ai-desk-tw.netlify.app/posts/{p.stem}",
    }


def _first(m):
    return m.group(1).strip() if m else None


def wrap_lines(text: str, font, max_width: int, draw) -> list[str]:
    """中英混排自動 wrap — 中文按字斷、英文按詞斷，盡量塞進每行。"""
    lines = []
    current = ""
    i = 0
    while i < len(text):
        ch = text[i]
        # 試著加進去
        test = current + ch
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current = test
            i += 1
        else:
            # 滿了，斷行
            if not current:
                # 一個字就超寬（極少見），強制塞
                current = ch
                i += 1
            lines.append(current.strip())
            current = ""
    if current:
        lines.append(current.strip())
    return lines


def render(post: dict, out_path: Path):
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img, "RGBA")

    # 載字體
    f_brand = load_font(F_DISPLAY, 32)
    f_brand.set_variation_by_axes([900])  # Inter Tight Black

    f_lockup = load_font(F_DISPLAY, 22)
    f_lockup.set_variation_by_axes([700])

    f_meta = load_font(F_DISPLAY, 18)
    f_meta.set_variation_by_axes([500])

    # chip 用 CJK 字體，否則中文字會變豆腐
    f_chip = load_font(F_CJK_BLACK, 15)

    f_title_zh = load_font(F_CJK_BLACK, 56)
    f_title_en = load_font(F_DISPLAY, 56)
    f_title_en.set_variation_by_axes([800])

    f_url = load_font(F_DISPLAY, 18)
    f_url.set_variation_by_axes([500])

    # 上下 padding
    PAD_X = 64
    PAD_Y = 56

    # ---- 左上 brand lockup ----
    # 鑽石符號
    diamond_x, diamond_y = PAD_X, PAD_Y + 6
    pts = [(diamond_x + 8, diamond_y), (diamond_x + 16, diamond_y + 8),
           (diamond_x + 8, diamond_y + 16), (diamond_x, diamond_y + 8)]
    draw.polygon(pts, fill=FG)
    draw.text((diamond_x + 28, diamond_y - 4), "AI DESK", font=f_brand, fill=FG)

    # ---- 右上 category chip ----
    chip_text = post["category"]
    chip_bbox = draw.textbbox((0, 0), chip_text, font=f_chip)
    chip_w = chip_bbox[2] - chip_bbox[0]
    chip_h = chip_bbox[3] - chip_bbox[1]
    chip_pad = 14
    chip_x = W - PAD_X - chip_w - chip_pad * 2
    chip_y = PAD_Y + 6
    draw.rectangle(
        [chip_x, chip_y, chip_x + chip_w + chip_pad * 2, chip_y + chip_h + chip_pad * 2 - 4],
        outline=FG, width=1
    )
    draw.text((chip_x + chip_pad, chip_y + chip_pad - 4), chip_text, font=f_chip, fill=FG)

    # ---- 中間標題（自動 wrap，最多 3 行） ----
    title = post["title"]
    # 移除「| AI DESK」尾巴
    title = re.sub(r"\s*\|\s*AI DESK\s*$", "", title).strip()
    # 移除前置「2026/04/27 ·」這種純日期前綴（OG 卡左下已寫日期）
    title = re.sub(r"^\d{4}/\d{2}/\d{2}\s*·\s*", "", title)

    title_max_w = W - PAD_X * 2 - 60
    # 試 60pt → 50pt → 42pt
    for size in (60, 54, 48, 42, 38):
        f_title = load_font(F_CJK_BLACK, size)
        lines = wrap_lines(title, f_title, title_max_w, draw)
        if len(lines) <= 3:
            break
    else:
        lines = lines[:3]
        if not lines[2].endswith("…"):
            lines[2] = lines[2][:-2] + "…"

    line_height = int(size * 1.32)
    title_total_h = len(lines) * line_height
    # 標題垂直置中（略偏上）
    title_y = (H - title_total_h) // 2 - 30
    for i, line in enumerate(lines):
        draw.text((PAD_X, title_y + i * line_height), line, font=f_title, fill=FG)

    # ---- 中間下分隔線 ----
    div_y = title_y + title_total_h + 28
    draw.line([(PAD_X, div_y), (W - PAD_X, div_y)], fill=(255, 255, 255, 60), width=1)

    # ---- 左下 edition + date ----
    f_edition = load_font(F_DISPLAY, 20)
    f_edition.set_variation_by_axes([700])
    bottom_y = H - PAD_Y - 26
    edition_text = f"N°{post['edition']:02d}  ·  {post['date']}  ·  FRI"
    # 簡化：從 date string 推 weekday
    try:
        from datetime import datetime as _dt
        wd_map = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
        wd = wd_map[_dt(int(post["year"]), int(post["mm"]), int(post["dd"])).weekday()]
        edition_text = f"N°{post['edition']:02d}  ·  {post['date']}  ·  {wd}"
    except Exception:
        pass
    draw.text((PAD_X, bottom_y), edition_text, font=f_edition, fill=FG)

    # ---- 右下 URL ----
    url_text = post["url_path"]
    url_bbox = draw.textbbox((0, 0), url_text, font=f_url)
    url_w = url_bbox[2] - url_bbox[0]
    draw.text((W - PAD_X - url_w, bottom_y + 2), url_text, font=f_url, fill=MUTE)

    # ---- 邊框（極細） ----
    draw.rectangle([8, 8, W - 8, H - 8], outline=(255, 255, 255, 18), width=1)

    img.save(out_path, "PNG", optimize=True)
    return out_path


def update_post_meta(post_html: Path, og_url: str):
    """更新該篇 HTML 的 og:image / twitter:image 指向新的 OG card"""
    text = post_html.read_text(encoding="utf-8")
    new_text = text
    new_text = re.sub(
        r'(<meta\s+property=["\']og:image["\']\s+content=["\'])[^"\']+(["\'])',
        rf'\1{og_url}\2', new_text
    )
    new_text = re.sub(
        r'(<meta\s+name=["\']twitter:image["\']\s+content=["\'])[^"\']+(["\'])',
        rf'\1{og_url}\2', new_text
    )
    if new_text != text:
        post_html.write_text(new_text, encoding="utf-8")
        return True
    return False


# ============================================================
# main
# ============================================================

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("html_path", nargs="?", help="Single article HTML to process")
    ap.add_argument("--all", action="store_true", help="Process all daily/weekly posts in posts/")
    args = ap.parse_args()

    targets: list[Path] = []
    if args.all:
        for p in POSTS.glob("*.html"):
            if p.name in ("index.html", "_template.html"):
                continue
            targets.append(p)
    elif args.html_path:
        targets.append(Path(args.html_path).resolve())
    else:
        ap.print_help()
        sys.exit(1)

    print(f"=== gen-og-card · {len(targets)} target(s) ===\n")

    latest_og = None
    for p in sorted(targets, reverse=True):
        info = parse_post(p)
        if not info:
            print(f"  skip (cannot parse filename): {p.name}")
            continue
        out = OG_DIR / f"{info['slug']}-og.png"
        render(info, out)
        og_url = f"https://ai-desk-tw.netlify.app/assets/og/{info['slug']}-og.png"
        updated = update_post_meta(p, og_url)
        size = out.stat().st_size
        print(f"  ✓ {info['slug']}  ({size // 1024} KB)  meta {'updated' if updated else 'unchanged'}")
        if latest_og is None:
            latest_og = out

    # 把最新一篇也覆寫 og-cover.png 當 fallback
    if latest_og and latest_og.exists():
        import shutil
        shutil.copy2(latest_og, DEFAULT_OG)
        print(f"\n  ✓ og-cover.png — overwritten with latest ({DEFAULT_OG.stat().st_size // 1024} KB)")

    print("\n=== done ===")


if __name__ == "__main__":
    main()
