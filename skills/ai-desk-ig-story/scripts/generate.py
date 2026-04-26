"""
ai-desk-ig-story · 從一篇 daily HTML 產 1080×1920 IG Story PNG + caption.txt

跑法：
  python3 generate.py <article.html> [output_dir]

例：
  python3 generate.py ~/Desktop/ai-desk-site/posts/2026-04-24-ai-daily.html

預設 output_dir = ~/Downloads/ai-desk-ig-stories/<date>/

產出：
  story.png   (1080×1920, mono brutalist)
  caption.txt (中英雙語 + hashtag)
"""
import re
import sys
from pathlib import Path
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont


# ============================================================
# Config
# ============================================================

W, H = 1080, 1920
MARGIN = 80
SITE_URL = "ai-desk-tw.netlify.app"
IG_HANDLE = "@ai_desk_0424"
COPYRIGHT = "© AI DESK · Independent Editorial"

SKILL_ROOT = Path(__file__).resolve().parent.parent
FONT_INTER = SKILL_ROOT / "fonts" / "InterTight-VF.ttf"
FONT_NOTO_BLACK = SKILL_ROOT / "fonts" / "NotoSansCJKtc-Black.otf"
FONT_NOTO_REG = SKILL_ROOT / "fonts" / "NotoSansCJKtc-Regular.otf"


# ============================================================
# Font helper
# ============================================================

def get_font(path: Path, size: int, weight: int = None) -> ImageFont.FreeTypeFont:
    f = ImageFont.truetype(str(path), size)
    if weight is not None:
        try:
            f.set_variation_by_axes([weight])
        except Exception:
            pass
    return f


# ============================================================
# Text wrapping (handles CJK 字符 not delimited by spaces)
# ============================================================

def measure(font: ImageFont.FreeTypeFont, text: str) -> int:
    bbox = font.getbbox(text)
    return bbox[2] - bbox[0]


def wrap_cjk(text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list:
    """逐字斷行。中文每個字單獨換行；英文以單詞為單位。"""
    lines = []
    line = ""
    i = 0
    while i < len(text):
        ch = text[i]
        # 英文 — 抓整個 word
        if ch.isascii() and ch.isalnum():
            word = ""
            while i < len(text) and text[i].isascii() and (text[i].isalnum() or text[i] in "-._/"):
                word += text[i]
                i += 1
            test = line + word
            if measure(font, test) <= max_width:
                line = test
            else:
                if line: lines.append(line.rstrip())
                line = word
        else:
            test = line + ch
            if measure(font, test) <= max_width:
                line = test
            else:
                if line: lines.append(line.rstrip())
                line = ch
            i += 1
    if line: lines.append(line.rstrip())
    return lines


# ============================================================
# HTML parser — 從 daily HTML 抽資料
# ============================================================

def parse_article(html: str) -> dict:
    def find(pattern, default=""):
        m = re.search(pattern, html, re.DOTALL)
        return m.group(1).strip() if m else default

    # title (純文字)
    title_html = find(r'<h1 class="post-title">(.*?)</h1>')
    title = re.sub(r'<[^>]+>', '', title_html)
    title = re.sub(r'\s+', ' ', title).strip()

    # short title (breadcrumb)
    title_short = find(r'<nav class="crumbs">[\s\S]*?</a><span[^>]*>/</span>\s*([^<\n]+)', title)
    title_short = title_short.replace('AI DESK', '').strip()

    # summary
    summary = find(r'<p class="post-sub">([\s\S]*?)</p>', '')
    summary = re.sub(r'<[^>]+>', '', summary).strip()

    # edition number (N°XX)
    edition = find(r'Edition N°(\d+)', '01')

    # date
    date_iso = find(r'<meta property="article:published_time" content="([^"]+)"', '')

    # key signals (從 aside.keypoints 內 ol > li > strong)
    keypoints_html = find(r'<aside class="keypoints">([\s\S]*?)</aside>', '')
    keypoints = []
    for li_match in re.finditer(r'<li>(.*?)</li>', keypoints_html, re.DOTALL):
        item = li_match.group(1)
        # 取 <strong> 內文字（前半）+ <strong> 後的破折號內容（後半）
        strong_m = re.search(r'<strong>(.*?)</strong>(.*)', item, re.DOTALL)
        if strong_m:
            head = re.sub(r'<[^>]+>', '', strong_m.group(1)).strip()
            tail = re.sub(r'<[^>]+>', '', strong_m.group(2)).strip()
            tail = re.sub(r'\s+', ' ', tail).lstrip('—— -').strip()
            keypoints.append({'head': head, 'tail': tail})
        else:
            text = re.sub(r'<[^>]+>', '', item).strip()
            keypoints.append({'head': text, 'tail': ''})

    return {
        'title': title,
        'title_short': title_short,
        'summary': summary,
        'edition': edition,
        'date_iso': date_iso,
        'keypoints': keypoints,
    }


# ============================================================
# Story image generator
# ============================================================

def render_story(article: dict, output_path: Path):
    img = Image.new('RGB', (W, H), (0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 1px border around (mono brutalist signature)
    draw.rectangle([(40, 40), (W - 40, H - 40)], outline=(255, 255, 255), width=2)

    # ---- TOP BAR ----
    top_y = 100
    # AI DESK lockup 左上
    f_lockup = get_font(FONT_INTER, 36, weight=900)
    draw.text((MARGIN + 30, top_y), "■ AI DESK", font=f_lockup, fill=(255, 255, 255))

    # 右上 N°XX
    f_edition = get_font(FONT_INTER, 32, weight=700)
    edition_text = f"N°{article['edition']}"
    edw = measure(f_edition, edition_text)
    draw.text((W - MARGIN - 30 - edw, top_y + 4), edition_text, font=f_edition, fill=(255, 255, 255))

    # ---- DATE row ----
    date_y = top_y + 60
    f_date = get_font(FONT_INTER, 24, weight=500)
    try:
        dt = datetime.fromisoformat(article['date_iso'])
        date_str = dt.strftime("%Y · %m · %d · %a").upper()
    except (ValueError, TypeError):
        date_str = "DAILY · AI 大事"
    draw.text((MARGIN + 30, date_y), date_str, font=f_date, fill=(138, 138, 138))

    # right of date row: "AI 大事"
    cat_text = "DAILY · AI 大事"
    f_cat = get_font(FONT_NOTO_REG, 22)
    cw = measure(f_cat, cat_text)
    draw.text((W - MARGIN - 30 - cw, date_y + 2), cat_text, font=f_cat, fill=(138, 138, 138))

    # divider line
    line_y = date_y + 60
    draw.line([(MARGIN + 30, line_y), (W - MARGIN - 30, line_y)], fill=(255, 255, 255), width=1)

    # ---- TITLE block ----
    title_y = line_y + 80

    # 用 Noto Black 處理中文顯示效果
    title_text = article['title']
    # 標題太長就用 short title
    if len(title_text) > 80:
        title_text = article['title_short'] or title_text[:60] + '...'

    f_title = get_font(FONT_NOTO_BLACK, 78)
    title_lines = wrap_cjk(title_text, f_title, W - 2 * (MARGIN + 30))
    # 限制最多 5 行 + 略縮放
    if len(title_lines) > 5:
        f_title = get_font(FONT_NOTO_BLACK, 64)
        title_lines = wrap_cjk(title_text, f_title, W - 2 * (MARGIN + 30))[:6]

    for i, line in enumerate(title_lines):
        y = title_y + i * (f_title.size + 8)
        draw.text((MARGIN + 30, y), line, font=f_title, fill=(255, 255, 255))

    title_block_end = title_y + len(title_lines) * (f_title.size + 8) + 40

    # ---- KEYPOINTS list ----
    kp_y = title_block_end + 40

    # 上方 small label "KEY SIGNALS"
    f_label = get_font(FONT_INTER, 22, weight=600)
    draw.text((MARGIN + 30, kp_y), "— KEY SIGNALS", font=f_label, fill=(138, 138, 138))
    kp_y += 50

    f_kp_head = get_font(FONT_NOTO_BLACK, 36)
    f_kp_tail = get_font(FONT_NOTO_REG, 28)

    for kp in article['keypoints'][:3]:
        # 標記 ◆
        draw.text((MARGIN + 30, kp_y + 4), "◆", font=f_kp_head, fill=(255, 255, 255))
        # head 文字 (黑體)
        head_lines = wrap_cjk(kp['head'], f_kp_head, W - 2 * (MARGIN + 30) - 60)
        for i, l in enumerate(head_lines[:2]):
            draw.text((MARGIN + 30 + 60, kp_y + i * (f_kp_head.size + 4)), l, font=f_kp_head, fill=(255, 255, 255))
        kp_y += len(head_lines[:2]) * (f_kp_head.size + 4) + 8

        # tail 文字 (淡色)
        if kp['tail']:
            tail_lines = wrap_cjk(kp['tail'], f_kp_tail, W - 2 * (MARGIN + 30) - 60)[:2]
            for i, l in enumerate(tail_lines):
                draw.text((MARGIN + 30 + 60, kp_y + i * (f_kp_tail.size + 2)), l, font=f_kp_tail, fill=(217, 217, 217))
            kp_y += len(tail_lines) * (f_kp_tail.size + 2)

        kp_y += 28  # spacing between keypoints

    # ---- BOTTOM block ----
    bottom_y = H - MARGIN - 220

    # divider
    draw.line([(MARGIN + 30, bottom_y), (W - MARGIN - 30, bottom_y)], fill=(255, 255, 255), width=1)

    # CTA — split EN + CJK 兩段，因為 Inter 不支援中文
    f_cta_en = get_font(FONT_INTER, 40, weight=800)
    f_cta_cjk = get_font(FONT_NOTO_BLACK, 36)
    en_text = "READ FULL"
    sep_text = " · "
    cjk_text = "全文＋源"
    draw.text((MARGIN + 30, bottom_y + 26), en_text, font=f_cta_en, fill=(255, 255, 255))
    en_w = measure(f_cta_en, en_text)
    draw.text((MARGIN + 30 + en_w, bottom_y + 30), sep_text, font=f_cta_cjk, fill=(255, 255, 255))
    sep_w = measure(f_cta_cjk, sep_text)
    draw.text((MARGIN + 30 + en_w + sep_w, bottom_y + 30), cjk_text, font=f_cta_cjk, fill=(255, 255, 255))

    # arrow
    f_arrow = get_font(FONT_INTER, 50, weight=900)
    draw.text((W - MARGIN - 30 - 50, bottom_y + 22), "→", font=f_arrow, fill=(255, 255, 255))

    # url
    f_url = get_font(FONT_INTER, 26, weight=500)
    draw.text((MARGIN + 30, bottom_y + 90), SITE_URL, font=f_url, fill=(138, 138, 138))

    # IG handle right-aligned
    ig_w = measure(f_url, IG_HANDLE)
    draw.text((W - MARGIN - 30 - ig_w, bottom_y + 90), IG_HANDLE, font=f_url, fill=(138, 138, 138))

    # copyright tiny
    f_copy = get_font(FONT_INTER, 20, weight=400)
    cw = measure(f_copy, COPYRIGHT)
    draw.text(((W - cw) // 2, bottom_y + 145), COPYRIGHT, font=f_copy, fill=(90, 90, 90))

    # 4 corner accents (小白色三角，brutalist 標誌)
    accent = 18
    for cx, cy in [(40, 40), (W - 40 - accent, 40), (40, H - 40 - accent), (W - 40 - accent, H - 40 - accent)]:
        draw.rectangle([(cx, cy), (cx + accent, cy + accent)], fill=(255, 255, 255))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path, 'PNG', optimize=True)
    print(f"✓ story PNG saved: {output_path} ({output_path.stat().st_size // 1024} KB)")


# ============================================================
# Caption generator
# ============================================================

def generate_caption(article: dict) -> str:
    edition = article['edition']
    title = article['title_short'] or article['title']
    summary = article['summary']

    # 抽 keypoints 第一行 head
    kp_lines = []
    for kp in article['keypoints'][:3]:
        kp_lines.append(f"◆ {kp['head']}")

    # 找 tags 從 article meta
    # 簡單 hashtag 策略：固定核心 + 從 keypoints 抽關鍵字
    base_tags = [
        "#AIDESK", "#AI大事", "#AINews", "#獨立編輯台",
        "#AIDailyBrief", "#AI", "#editorial", "#monobrutalist"
    ]
    # 從文章內容抓專有名詞 hashtag
    content_tags = []
    for keyword, tag in [
        ('GPT-5.5', '#GPT55'), ('GPT-5', '#GPT5'),
        ('Claude Code', '#ClaudeCode'), ('Anthropic', '#Anthropic'),
        ('OpenAI', '#OpenAI'), ('postmortem', '#postmortem'),
        ('open-source', '#opensource'), ('開源', '#opensource'),
        ('deepfake', '#deepfake'), ('Karpathy', '#Karpathy'),
        ('LLM', '#LLM'), ('agentic', '#agentic'),
    ]:
        if keyword.lower() in title.lower() or keyword.lower() in summary.lower():
            content_tags.append(tag)

    all_tags = list(dict.fromkeys(base_tags + content_tags))  # de-dup

    caption = f"""{title}

— N°{edition} · {datetime.now().strftime('%Y/%m/%d')} —

{summary}

{chr(10).join(kp_lines)}

····

全文 · 附源 · 附判斷
ai-desk-tw.netlify.app

{' '.join(all_tags)}
"""
    return caption


# ============================================================
# Main
# ============================================================

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 generate.py <article.html> [output_dir]")
        sys.exit(1)

    article_path = Path(sys.argv[1]).expanduser().resolve()
    if not article_path.exists():
        print(f"❌ article not found: {article_path}")
        sys.exit(1)

    # Default output dir: ~/Downloads/ai-desk-ig-stories/<YYYY-MM-DD>/
    if len(sys.argv) >= 3:
        output_dir = Path(sys.argv[2]).expanduser().resolve()
    else:
        slug = article_path.stem  # e.g. 2026-04-24-ai-daily
        date_part = '-'.join(slug.split('-')[:3])  # 2026-04-24
        output_dir = Path.home() / "Downloads" / "ai-desk-ig-stories" / date_part

    output_dir.mkdir(parents=True, exist_ok=True)

    html = article_path.read_text(encoding='utf-8')
    article = parse_article(html)

    print(f"\n=== parsed article ===")
    print(f"  title: {article['title'][:80]}")
    print(f"  edition: N°{article['edition']}")
    print(f"  keypoints: {len(article['keypoints'])}")
    print()

    # Render PNG
    story_path = output_dir / "story.png"
    render_story(article, story_path)

    # Caption
    caption_path = output_dir / "caption.txt"
    caption_path.write_text(generate_caption(article))
    print(f"✓ caption saved: {caption_path}")

    print(f"\n=== output dir ===")
    print(f"  {output_dir}")
    print(f"\n打開 {output_dir} 把 story.png 上傳 IG Story，caption.txt 內容貼到說明欄。")


if __name__ == '__main__':
    main()
