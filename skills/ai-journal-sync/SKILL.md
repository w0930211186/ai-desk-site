---
name: ai-journal-sync
description: 把 Notion「AI DESK 編輯台」database 裡 Status=ready-to-ship 的文章 同步到 AI DESK 官網 — 塞進 /posts/_template.html → 寫出 /posts/YYYY-MM-DD-slug.html → 重新組 /posts/index.html 的 FEED 區 → 更新首頁 latest 6 張卡 → git commit push → Netlify 自動部署。當使用者說「同步官網 / 發文章到官網 / ship to site / journal sync / 把 Notion 的文章發出去 / 更新 AI DESK」等類似指令時觸發 即使沒明確說「用 skill」。
---

# ai-journal-sync

獨立 AI 編輯台的官網同步機器。從 Notion source of truth 拉到 Git-backed 靜態站 完整管線。

## 觸發詞

中文：同步官網、發官網、把 Notion 發出去、更新 journal、更新 AI DESK、ship 官網、上 journal、文章發布

English: sync journal, publish article, ship to site, deploy post, update AI DESK, journal sync

## 依賴

**環境變數**（`.env` 或 Netlify env）
```
NOTION_TOKEN=secret_xxxxxxxx
NOTION_DATABASE_ID=xxxxxxxxxxxx
GITHUB_TOKEN=ghp_xxxx
GITHUB_REPO=username/ai-desk-site
GIT_AUTHOR_NAME=ai-desk-bot
GIT_AUTHOR_EMAIL=bot@ai-desk-tw.netlify.app
```

**檔案依賴**
- `posts/_template.html` — 帶 placeholder 的骨架（v2.1 已剝除 DOCTYPE 註解，docs 在 sibling `_template-readme.md`）
- `posts/index.html` — 有 `<!-- POSTS-INJECTION-START/END -->` 標記
- `index.html` — 有 `<!-- FEED-INJECTION-START/END -->` 標記
- `sitemap.xml` — 會追加新 URL

## 執行流程

### 1. 從 Notion 撈 candidate
查詢 database：`filter: { Status: { equals: "ready-to-ship" } }`
- 如果 0 筆 → 沒事做 exit 0
- 如果 > 1 筆 → 按 Publish Date 從早到晚處理

### 2. 渲染單篇文章
對每一筆 row：
1. 撈 Notion blocks → 轉 HTML（見 placeholder 對照表）
2. 讀 `_template.html`
3. 替換 placeholder：`{{TITLE}}` `{{TITLE_HTML}}` `{{TITLE_SHORT}}` `{{SUMMARY}}` `{{SLUG}}` `{{DATE_ISO}}` `{{DATE_DISPLAY}}` `{{DAY}}` `{{EDITION_NUM}}` `{{CATEGORY}}` `{{CATEGORY_LABEL}}` `{{TAG_CHIPS}}` `{{WARNING_BANNER}}` `{{BODY_HTML}}` `{{PREV_NEXT_NAV}}` `{{KEYWORDS}}`
4. **【P0 防呆 · v2.1 新增】Strip & Smoke Test**（見下方專段）
5. 寫到 `posts/{SLUG}.html`

### 3. 回填 prev/next 連結
掃 `posts/` 下所有 HTML 按日期排序，回填每篇 prev / next。每次 sync 都重算（idempotent）。

組 `{{PREV_NEXT_NAV}}` 的內容（v2.1 改成動態注入，不再是註解 toggle）：
```html
<nav class="prev-next">
  <a href="{prev_slug}.html" class="prev"><span class="label">← 上一篇</span><span class="title">{prev_title}</span></a>
  <a href="{next_slug}.html" class="next"><span class="label">下一篇 →</span><span class="title">{next_title}</span></a>
</nav>
```
若沒有 prev / next，對應 `<a>` 整段省略；如果兩個都沒有，整個 `{{PREV_NEXT_NAV}}` 替換成空字串。

### 4. 重建 /posts/index.html FEED 區
讀全部 posts / 按 YYYY-MM 分組 / 產生 `.month-block` 的 `.post-row` HTML / 替換兩標記之間的內容。

### 5. 更新 /index.html 首頁 feed
拿最新 6 筆（按日期 desc），第 1 筆放 c1 卡（非 ghost），其餘放 c2-c6。

### 6. 更新 /sitemap.xml
加入新 URL entry。

### 7. git 推送
```
git add posts/<slug>.html posts/index.html index.html sitemap.xml
git commit -m "post: <title> [YYYY-MM-DD]"
git push origin main
```

### 8. 寫回 Notion
- Status: `ready-to-ship` → `shipped`
- Site URL: 填入
- Shipped At: 當下時間

### 9. 鏈式觸發
觸發 `ai-ig-render` skill（如果存在）

---

## 🛡️ P0 防呆 · Strip & Smoke Test（v2.1 新增）

**背景**：v2.0 範本把 placeholder 文件放在 `<!DOCTYPE>` 與 `<html>` 之間的 HTML 註解裡。
若 `{{BODY_HTML}}` 內含任何 `-->`（例如 `<!-- 今日重點方向 -->`），字串替換後會提前關閉外層註解，
整段 body 被 HTML parser hoist 到 `<body>` 之前以 raw HTML 渲染：DOM 雙倍、橫向爆版、SEO 重複內容、a11y 螢幕閱讀器讀兩次。
v2.1 已從 `_template.html` 剝除該註解，但**仍保留以下兩道保險**，避免新貢獻者再踩。

### Step 4a · Strip DOCTYPE-to-html 之間的所有註解

每篇文章 render 完成後、寫檔之前，跑這段：

```python
import re

def strip_pre_html_comments(html: str) -> str:
    """砍掉 <!DOCTYPE> 與 <html> 之間的所有 HTML 註解（保留 DOCTYPE 與 <html> 本身）"""
    return re.sub(
        r'(<!DOCTYPE[^>]*>)\s*(?:<!--.*?-->\s*)+(?=<html\b)',
        r'\1\n',
        html,
        count=1,
        flags=re.DOTALL | re.IGNORECASE,
    )

rendered = strip_pre_html_comments(rendered)
```

### Step 4b · 渲染後 smoke test（assert 不能炸）

```python
def smoke_test(html: str, slug: str) -> None:
    checks = [
        # P0 雙倍渲染檢測
        (html.count('<aside class="keypoints"'), 1, "keypoints 必須恰好 1 個"),
        (html.lower().count('<article class="post"'), 1, "article.post 必須恰好 1 個"),
        # DOCTYPE 後直接 <html>（中間最多空白）
        (bool(re.search(r'<!DOCTYPE[^>]*>\s*<html\b', html, re.IGNORECASE)), True, "DOCTYPE 與 <html> 之間不能有任何內容"),
        # 沒有未替換的 placeholder
        (bool(re.search(r'\{\{[A-Z_]+\}\}', html)), False, "不能有未替換的 {{PLACEHOLDER}}"),
    ]
    failures = [(actual, want, msg) for actual, want, msg in checks if actual != want]
    if failures:
        raise BuildError(
            f"[{slug}] smoke test failed:\n" +
            "\n".join(f"  - {msg} (got {actual}, want {want})" for actual, want, msg in failures)
        )
```

### Step 4c · 連結驗活（防止假源 ID）

```python
import requests
def verify_links(html: str) -> None:
    for url in re.findall(r'href="(https?://[^"]+)"', html):
        # HN item ID 必須是純數字（防止 AI 自編 ?id=gpt55 這類假連結）
        m = re.search(r'news\.ycombinator\.com/item\?id=([^&]+)', url)
        if m and not m.group(1).isdigit():
            raise BuildError(f"假 HN item id（必須純數字）: {url}")
        # 主要外連 HEAD 一下，5xx / 404 fail
        try:
            r = requests.head(url, timeout=5, allow_redirects=True)
            if r.status_code >= 400:
                raise BuildError(f"Dead link {r.status_code}: {url}")
        except requests.RequestException as e:
            print(f"  warn: 無法驗活 {url}: {e}")  # CDN 反 bot 太多，只警告不 fail
```

### Step 4d · build-time bash smoke test（push 前最後一道）

`scripts/smoke.sh`（CI 或 pre-push hook 用）：

```bash
#!/usr/bin/env bash
set -e
for f in posts/*.html; do
  [[ "$(basename $f)" == "_template.html" || "$(basename $f)" == "index.html" ]] && continue
  count=$(grep -c '<aside class="keypoints"' "$f" || true)
  [ "$count" -eq 1 ] || { echo "❌ $f: keypoints=$count (want 1)"; exit 1; }
  fig=$(grep -c '<figure' "$f" || true)
  [ "$fig" -le 10 ] || { echo "❌ $f: figure=$fig (want ≤ 10，超過代表雙倍渲染)"; exit 1; }
done
echo "✓ smoke test passed"
```

---

## Notion blocks → HTML 對照表

| Notion block | HTML output |
|---|---|
| heading_2 | `<h2><span class="num">N°XX</span>{text}</h2>`（N°XX 取 Edition Num） |
| heading_3 | `<h3>{text}</h3>` |
| paragraph | `<p>{inline}</p>` |
| bulleted_list_item | 組成 `<ul><li>{inline}</li></ul>` |
| numbered_list_item | 組成 `<ol><li>{inline}</li></ol>` |
| quote | `<blockquote>{inline}</blockquote>` |
| code | `<pre><code class="language-{lang}">{text}</code></pre>` |
| image | 第一張用 `<figure><img ... fetchpriority="high"><figcaption>{caption}</figcaption></figure>`，後續用 `loading="lazy"` |
| divider | `<hr>` |

**Inline rich text**：
- `bold=true` → `<strong>`
- `italic=true` → `<em>`（outline 效果）
- `code=true` → `<code>`
- `link.url` → `<a href="{url}" target="_blank" rel="noopener">`

## 錯誤處理

| 錯誤 | 動作 |
|---|---|
| Notion API timeout (3 次重試後) | email draft 通知 + status 退回 ready |
| Template 檔案不存在 | email draft + 停止 |
| **smoke test fail（v2.1 新）** | **不 commit + email draft 附 detected issues + 退回 Notion ready** |
| **連結驗活 fail（v2.1 新）** | **不 commit + email draft 列出死連結** |
| git push fail (auth/conflict) | 保留 local commit + email draft |
| Netlify build 失敗通知 | 監聽 Netlify webhook（v3 再做） |

## Gmail draft 失敗通知 template

```
Subject: [AI DESK · 🔴] ai-journal-sync · <title> 發布失敗

時間：{ISO}
Skill：ai-journal-sync
狀態：🔴
事件：Notion row "{title}" sync 失敗

— 發生什麼 —
{error message}

— Rick 要做什麼 —
[ ] 打開 Notion row: {notion_url}
[ ] 確認 Status 已退回 ready
[ ] 根據 error message 修正
[ ] 手動觸發「同步官網」重跑
```

## 冪等性保證

同一個 slug 重跑多次結果一致：
- 已存在的 `posts/{slug}.html` 覆寫（不累積）
- posts/index.html 完全重建 feed 區（不追加）
- Sitemap 去重
- git commit 如果沒 diff 自動 skip

## 測試步驟

1. 建一個 Notion test row with minimal content
2. **故意在 body 內寫 `<!-- 今日重點方向 -->` 之類的 HTML 註解**（測 P0 防呆）
3. Status 手動設 `ready-to-ship`
4. 跑 skill
5. 檢查：
   - [ ] `posts/{slug}.html` 存在且 HTTP 200
   - [ ] **`grep -c '<aside class="keypoints"' posts/{slug}.html` == 1**（不是 2 不是 0）
   - [ ] **DOCTYPE 後第 1 個非空白 char 是 `<html>`**
   - [ ] **`{{` 不出現在輸出（沒有未替換 placeholder）**
   - [ ] `posts/index.html` 有新 row
   - [ ] `index.html` 首頁 c1 卡更新
   - [ ] `sitemap.xml` 有新 entry
   - [ ] git log 有新 commit
   - [ ] Notion Status 變 `shipped`
   - [ ] Notion Site URL 欄位有值

## 實作檔案結構

```
skills/ai-journal-sync/
  ├── SKILL.md         (本檔)
  ├── scripts/
  │   ├── sync.py      (主入口)
  │   ├── notion_to_html.py
  │   ├── template.py  (含 strip_pre_html_comments + smoke_test)
  │   ├── feed_builder.py
  │   ├── git_ops.py
  │   ├── verify.py    (連結驗活)
  │   └── smoke.sh     (push 前最後一道 bash 檢查)
  └── tests/
      ├── test_render.py
      └── test_p0_safety.py  (重現 v2.0 雙倍渲染 bug，回歸測試)
```
