"""
ai-desk-ig-auto-post · 主流程協調器

這個 script 不直接跑（Cowork Claude session 需要 Chrome MCP 工具）—
而是給 Cowork Claude 讀取的「執行劇本」，列出每個步驟該做什麼。

跑法（Cowork 環境內）：
1. Cowork Claude 讀本檔
2. 依步驟順序呼叫對應的 Chrome MCP 工具 + send_telegram.py

或直接互動：
  「跑 ai-desk-ig-auto-post」

這個 script 也可以單獨在使用者 Mac 上 dry-run 測試（不真的點分享）：
  python3 orchestrate.py --dry-run
"""
import sys
import os
import base64
import json
import re
from pathlib import Path
from datetime import datetime


CONFIG = {
    'asset_id': '1141294485727223',  # AI DESK Page asset portfolio
    'business_id': '1274367634384629',
    'page_id': '61562839956251',
    'ig_handle': 'ai_desk_0424',
    'site_url': 'https://ai-desk-tw.netlify.app',
    'latest_url': 'https://ai-desk-tw.netlify.app/latest',
    'story_composer_url': 'https://business.facebook.com/latest/story_composer/',
    'feed_composer_url': 'https://business.facebook.com/latest/composer/',
    'tg_bot_token_env': 'TELEGRAM_BOT_TOKEN',
    'tg_chat_id_env': 'TELEGRAM_CHAT_ID',
    'chunk_size': 18000,
}


def find_latest_daily(repo_root: Path = None) -> Path:
    """找最新一篇 daily HTML（排除 _template / index）"""
    if repo_root is None:
        repo_root = Path.home() / 'Desktop' / 'ai-desk-site'
    posts = repo_root / 'posts'
    candidates = sorted(
        [f for f in posts.glob('*.html') if f.name not in ('_template.html', 'index.html')],
        reverse=True,
    )
    return candidates[0] if candidates else None


def get_today_story_path(date_str: str = None) -> Path:
    if date_str is None:
        date_str = datetime.now().strftime('%Y-%m-%d')
    return Path.home() / 'Downloads' / 'ai-desk-ig-stories' / date_str / 'story.png'


def chunk_image(png_path: Path, chunk_size: int = None) -> list:
    """把 PNG 讀成 base64 + 切 chunks 給 JS 注入用"""
    if chunk_size is None:
        chunk_size = CONFIG['chunk_size']
    b64 = base64.b64encode(png_path.read_bytes()).decode()
    return [b64[i:i + chunk_size] for i in range(0, len(b64), chunk_size)]


def build_inject_chunk_js(idx: int, chunk: str) -> str:
    """產 JS 把 chunk 設到 window var"""
    # 用 JSON-encode 安全處理 chunk 字串
    return f'window.b64_{idx} = {json.dumps(chunk)};'


def build_assemble_drop_js() -> str:
    """組合 chunks + 建 File + dispatch drop 到 Meta drop zone"""
    return '''((async () => {
  const chunks = [];
  for (let i = 0; window["b64_" + i] !== undefined; i++) chunks.push(window["b64_" + i]);
  if (chunks.length === 0) return { error: "no chunks" };
  const b64 = chunks.join("");

  const bytes = Uint8Array.from(atob(b64), c => c.charCodeAt(0));
  const file = new File([bytes], "story.png", { type: "image/png", lastModified: Date.now() });

  const zone = Array.from(document.querySelectorAll("div")).find(d =>
    /將相片或影片拖放到這裡|drag and drop/i.test(d.textContent) && d.textContent.length < 300 && d.offsetParent
  );
  if (!zone) return { error: "no drop zone", chunks: chunks.length };

  const dt = new DataTransfer();
  dt.items.add(file);
  for (const e of ["dragenter", "dragover", "drop"]) {
    zone.dispatchEvent(new DragEvent(e, { bubbles: true, cancelable: true, dataTransfer: dt }));
  }

  for (let i = 0; window["b64_" + i] !== undefined; i++) delete window["b64_" + i];

  return { ok: true, fileSize: file.size, chunksUsed: chunks.length };
})())'''


def build_click_share_js() -> str:
    """找並點「分享」按鈕"""
    return '''((async () => {
  await new Promise(r => setTimeout(r, 500));
  const btn = Array.from(document.querySelectorAll('div[role="button"], button'))
    .find(b => b.textContent.trim() === "分享" && b.offsetParent);
  if (!btn) return { error: "no share button", buttons: Array.from(document.querySelectorAll('div[role="button"], button')).map(b => b.textContent.trim()).filter(t => t).slice(0, 10) };
  btn.click();
  return { ok: true };
})())'''


def build_check_success_js() -> str:
    """確認「你的限時動態已發佈」訊息"""
    return '''((async () => {
  await new Promise(r => setTimeout(r, 4000));
  const text = document.body.innerText;
  return {
    success: text.includes("你的限時動態已發佈") || text.includes("Your story has been published"),
    bodySnippet: text.slice(0, 600).replace(/\\s+/g, " ")
  };
})())'''


def build_telegram_success_msg(slug: str, edition: str, parts_done: list = None) -> str:
    article_url = f"{CONFIG['site_url']}/posts/{slug}"
    if parts_done is None:
        parts_done = ['story', 'feed']
    parts_lines = []
    if 'story' in parts_done:
        parts_lines.append(f"✓ Story · IG @{CONFIG['ig_handle']} + FB")
    if 'feed' in parts_done:
        parts_lines.append(f"✓ Feed Post · IG @{CONFIG['ig_handle']} + FB")
    parts_str = "\n".join(parts_lines)
    return (
        "✅ *AI DESK · IG/FB 自動發布完成*\n\n"
        f"N°{edition} · {datetime.now().strftime('%m/%d')} daily\n"
        f"{parts_str}\n\n"
        f"🌐 全文：{article_url}\n"
        f"🔗 Latest：{CONFIG['latest_url']}\n"
        f"🔗 IG：instagram.com/{CONFIG['ig_handle']}"
    )


# ============================================================
# Feed Post (v2 加) — 同 story.png 再發一次成 IG/FB Feed Post
# ============================================================

def build_paste_caption_js(caption_text: str) -> str:
    """找 caption textarea / contenteditable，貼進去 caption 內容"""
    safe_caption = json.dumps(caption_text)
    return f'''((async () => {{
  await new Promise(r => setTimeout(r, 800));
  const text = {safe_caption};
  // 1) 標準 textarea
  let target = Array.from(document.querySelectorAll('textarea'))
    .find(t => t.offsetParent && (/撰寫|貼文|Write|caption/i.test(t.placeholder + " " + (t.getAttribute('aria-label') || ''))));
  // 2) 退而求其次：contenteditable
  if (!target) {{
    target = Array.from(document.querySelectorAll('div[contenteditable="true"], div[role="textbox"]'))
      .find(d => d.offsetParent && d.getBoundingClientRect().width > 200);
  }}
  if (!target) return {{ error: "no caption field", textareas: document.querySelectorAll('textarea').length, editables: document.querySelectorAll('[contenteditable="true"]').length }};
  target.focus();
  if (target.tagName === "TEXTAREA") {{
    target.value = text;
    target.dispatchEvent(new Event("input", {{ bubbles: true }}));
    target.dispatchEvent(new Event("change", {{ bubbles: true }}));
  }} else {{
    // contenteditable
    document.execCommand("insertText", false, text);
  }}
  return {{ ok: true, length: text.length }};
}})())'''


def build_click_publish_js() -> str:
    """找並點 Feed Post 的「發佈/發布/Publish/Post」按鈕"""
    return '''((async () => {
  await new Promise(r => setTimeout(r, 800));
  const btn = Array.from(document.querySelectorAll('div[role="button"], button'))
    .find(b => /^(發佈|發布|Publish|Post)$/.test(b.textContent.trim()) && b.offsetParent && !b.getAttribute("aria-disabled"));
  if (!btn) return { error: "no publish button", buttons: Array.from(document.querySelectorAll('div[role="button"], button')).map(b => b.textContent.trim()).filter(t => t).slice(0, 15) };
  btn.click();
  return { ok: true };
})())'''


def build_check_feed_success_js() -> str:
    """確認 Feed Post 發佈成功"""
    return '''((async () => {
  await new Promise(r => setTimeout(r, 5000));
  const text = document.body.innerText;
  return {
    success: /已發佈|貼文已發|published|Posted/i.test(text),
    bodySnippet: text.slice(0, 800).replace(/\\s+/g, " ")
  };
})())'''


def build_feed_caption(title: str, edition: str, summary_zh: str, summary_en: str,
                       keypoints: list, hashtags: list = None) -> str:
    """組 Feed Post caption 文字（雙語短摘要 + keypoints + hashtag）"""
    base_tags = [
        "#AIDESK", "#AI大事", "#AINews", "#獨立編輯台", "#AIDailyBrief",
        "#AI", "#editorial", "#monobrutalist"
    ]
    if hashtags:
        base_tags.extend(hashtags)
    tags_line = " ".join(base_tags)

    kp_lines = "\n".join(f"◆ {k}" for k in keypoints[:3])
    date_str = datetime.now().strftime('%Y/%m/%d')

    return (
        f"{title}\n\n"
        f"— N°{edition} · {date_str} · AI DESK —\n\n"
        f"{summary_zh}\n\n"
        f"{summary_en}\n\n"
        f"{kp_lines}\n\n"
        "····\n\n"
        f"全文 → bio · {CONFIG['latest_url'].replace('https://', '')}\n\n"
        f"{tags_line}"
    )


def build_telegram_failure_msg(reason: str) -> str:
    return (
        "⚠️ *AI DESK · IG 自動發布失敗*\n\n"
        f"原因：{reason}\n\n"
        "📱 *手動 backup（30 秒）*：\n"
        "1. 打開 Telegram 看上面的 story.png\n"
        "2. 長按圖 → Save to Photos\n"
        "3. IG → 加限動 → 選圖 → 發\n\n"
        "Mac Chrome 開著嗎？FB 還登著嗎？"
    )


# ============================================================
# Cowork 執行清單（給 Cowork Claude 讀）
# ============================================================

EXECUTION_PLAN = """
## ai-desk-ig-auto-post 執行清單（給 Cowork Claude 照跑）

### 0. 前置檢查
- [ ] 用戶 Mac Chrome 連線狀態：tabs_context_mcp
- [ ] FB 已登入：navigate https://www.facebook.com/ 看 user menu
- [ ] 若 Chrome 沒開或 FB 沒登入 → 推 Telegram 警示 + 結束

### 1. 確認 daily 文章存在
- [ ] curl https://raw.githubusercontent.com/w0930211186/ai-desk-site/main/posts/<today>-daily.html
- [ ] 抽 title / edition / summary

### 2. 產 story.png
- [ ] 跑 ai-desk-ig-story skill
- [ ] 確認檔案在 ~/Downloads/ai-desk-ig-stories/<today>/story.png

### 3. 開 Business Suite
- [ ] navigate to https://business.facebook.com/latest/story_composer/?asset_id=1141294485727223&business_id=1274367634384629
- [ ] 等 3 秒 page ready

### 4. 注入圖片 chunks
- [ ] read story.png → base64 → 切 chunks
- [ ] 對每個 chunk: javascript_exec "window.b64_<i> = '<chunk>'"
- [ ] javascript_exec assemble_drop_js → drop file 到 zone

### 5. 等上傳完成
- [ ] 等 8 秒
- [ ] javascript_exec 確認預覽出現

### 6. Story · 點分享
- [ ] javascript_exec click_share_js
- [ ] 等 5 秒，javascript_exec check_success_js
- [ ] 確認「你的限時動態已發佈」

### 7. Feed Post · 開 Composer（v2 加）
- [ ] navigate to https://business.facebook.com/latest/composer/?asset_id=1141294485727223&business_id=1274367634384629
- [ ] 等 3 秒
- [ ] 同樣方式 inject + drop story.png（同一張）
- [ ] 等 6 秒等預覽

### 8. Feed Post · 貼 caption
- [ ] 從 ~/Downloads/ai-desk-ig-stories/<today>/caption.txt 讀
- [ ] 或呼叫 build_feed_caption(title, edition, summary_zh, summary_en, keypoints)
- [ ] javascript_exec build_paste_caption_js(caption)

### 9. Feed Post · 點發佈
- [ ] javascript_exec build_click_publish_js()
- [ ] 等 6 秒
- [ ] javascript_exec build_check_feed_success_js()

### 10. Telegram 通知
- [ ] 兩篇都成功 → build_telegram_success_msg(slug, edition, ['story', 'feed'])
- [ ] Story 成功 Feed 失敗 → build_telegram_success_msg(slug, edition, ['story']) + 失敗備註
- [ ] 都失敗 → build_telegram_failure_msg(reason)

### 11. 結束
- [ ] log 結果到 ~/.config/ai-desk/ig-auto-post.log
"""


if __name__ == '__main__':
    if '--print-plan' in sys.argv:
        print(EXECUTION_PLAN)
    elif '--dry-run' in sys.argv:
        latest = find_latest_daily()
        story = get_today_story_path()
        chunks = chunk_image(story) if story.exists() else []
        print(f'latest daily: {latest}')
        print(f'story path:   {story}')
        print(f'story exists: {story.exists()}')
        print(f'chunks:       {len(chunks)} (each {CONFIG["chunk_size"]} chars)')
        print(f'\n--- assemble JS preview (first 200 chars) ---')
        print(build_assemble_drop_js()[:200] + '...')
    else:
        print(__doc__)
        print('\nUse --print-plan to see Cowork execution checklist')
        print('Use --dry-run to test locally')
