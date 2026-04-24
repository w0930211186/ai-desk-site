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
- `posts/_template.html` — 帶 placeholder 的骨架
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
3. 替換 placeholder：`{{TITLE}}` `{{TITLE_SHORT}}` `{{SUMMARY}}` `{{SLUG}}` `{{DATE_ISO}}` `{{DATE_DISPLAY}}` `{{DAY}}` `{{EDITION_NUM}}` `{{CATEGORY}}` `{{CATEGORY_LABEL}}` `{{TAG_CHIPS}}` `{{WARNING_BANNER}}` `{{BODY_HTML}}` `{{PREV_SLUG}}` `{{PREV_TITLE}}` `{{NEXT_SLUG}}` `{{NEXT_TITLE}}` `{{KEYWORDS}}`
4. 寫到 `posts/{SLUG}.html`

### 3. 回填 prev/next 連結
掃 `posts/` 下所有 HTML 按日期排序，回填每篇 prev / next。每次 sync 都重算（idempotent）。

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
| image | `<figure><img src="{url}" alt="{caption}"><figcaption>{caption}</figcaption></figure>` |
| divider | `<hr>` |

**Inline rich text**：
- `bold=true` → `<strong>`
- `italic=true` → `<em>`（outline 效果）
- `code=true` → `<code>`
- `link.url` → `<a href="{url}">`

## 錯誤處理

| 錯誤 | 動作 |
|---|---|
| Notion API timeout (3 次重試後) | email draft 通知 + status 退回 ready |
| Template 檔案不存在 | email draft + 停止 |
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
2. Status 手動設 `ready-to-ship`
3. 跑 skill
4. 檢查：
   - [ ] `posts/{slug}.html` 存在且 HTTP 200
   - [ ] `posts/index.html` 有新 row
   - [ ] `index.html` 首頁 c1 卡更新
   - [ ] `sitemap.xml` 有新 entry
   - [ ] git log 有新 commit
   - [ ] Notion Status 變 `shipped`
   - [ ] Notion Site URL 欄位有值

## 實作檔案結構（下一輪會填）

```
skills/ai-journal-sync/
  ├── SKILL.md        (本檔)
  ├── scripts/
  │   ├── sync.py     (主入口)
  │   ├── notion_to_html.py
  │   ├── template.py
  │   ├── feed_builder.py
  │   └── git_ops.py
  └── tests/
      └── test_render.py
```
