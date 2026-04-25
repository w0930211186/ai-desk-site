# AI DESK · Article Template (v2.1)

`_template.html` 是 ai-journal-sync skill 用來產生每篇 daily 文章的骨架。

## v2.0 → v2.1 變更

修掉 P0 級 bug：原本把 placeholder 文件寫在 `<!DOCTYPE html>` 與 `<html>` 之間的 HTML 註解裡，
當 AI 替換 `{{BODY_HTML}}` 時兩處都換，body 內任何 `-->` 都會提前關閉外層註解，
導致整篇 body 被 hoist 到 `<body>` 之前以 raw HTML 渲染（雙倍 DOM、橫向爆版、SEO 重複）。

**修法**：

1. 把整段 placeholder 文件搬出 `_template.html`，改放這個 sibling `.md` 檔（你正在讀的）
2. `_template.html` 從 DOCTYPE 直接接 `<html>`，0 個 HTML 註解
3. PREV/NEXT 註解區塊改成 `{{PREV_NEXT_NAV}}` 動態 placeholder（skill 決定要不要注入）
4. ai-journal-sync skill 的 publish 流程加 strip + smoke test 雙保險（見 SKILL.md）

---

## Placeholder 規範

| Placeholder | 說明 | 範例 |
|---|---|---|
| `{{TITLE}}` | 文章標題 純文字 | `2026/04/24 · AI 大事 · GPT-5.5、Claude Code postmortem` |
| `{{TITLE_HTML}}` | 標題含 `<em>inline outline</em>` 排版版本（optional 若空 fallback `{{TITLE}}`） | |
| `{{TITLE_SHORT}}` | breadcrumb 用的短標題（≤ 24 字） | `04/24 AI 大事` |
| `{{SUMMARY}}` | 摘要 140-160 字（meta description / og:description 共用） | |
| `{{SLUG}}` | URL slug 格式 `YYYY-MM-DD-<topic-ascii>` | `2026-04-24-ai-daily` |
| `{{DATE_ISO}}` | 發布日期 ISO8601 | `2026-04-24T07:00:00+08:00` |
| `{{DATE_DISPLAY}}` | 顯示用 | `2026 · 04 · 24` |
| `{{DAY}}` | 星期縮寫 | `FRI` |
| `{{EDITION_NUM}}` | 期數 | `01` / `02` / `03` |
| `{{CATEGORY}}` | 主分類 | `news` / `tools` / `intel` / `meta` |
| `{{CATEGORY_LABEL}}` | 中文分類標籤 | `News · 新聞` / `Tools · 工具` / `Intel · 情報` / `Meta · 站務` |
| `{{TAG_CHIPS}}` | tag HTML 片段 | `<span class="tag">News · 新聞</span><span class="tag mute">Anthropic</span>` |
| `{{KEYWORDS}}` | meta keywords 額外字 | `GPT-5.5, Claude Code, agentic coding` |
| `{{WARNING_BANNER}}` | brief-ship 塗銷模式（optional 沒事留空字串） | |
| `{{BODY_HTML}}` | 文章主體 semantic HTML（h2/h3/p/ul/ol/blockquote/img/figure） | |
| `{{PREV_NEXT_NAV}}` | 上下篇導覽 HTML 片段（skill 決定空字串或 `<nav class="prev-next">...</nav>`） | |

## body HTML 慣例

- `<h2>` 自動大寫，可加 `<span class="num">N°XX</span>` 編號
- `<em>` 是 outline 效果（透明字 + 外描邊），不是斜體
- `<ul>` 為 ◆ bullets，不需寫 list-style
- `<blockquote>` 全寬橫線 + ❝ 開口，用於金句
- inline `<code>` / `<pre>` 都有 token 樣式

## 圖片

- 任何 `<figure><img>` 都會自動 `max-width: 100%`（CSS reset 已蓋）
- 第一張 figure 加 `fetchpriority="high"`，其餘加 `loading="lazy" decoding="async"`
- 大圖建議 `<picture>` 雙格式：
  ```html
  <figure>
    <picture>
      <source srcset="../assets/news/foo.webp" type="image/webp">
      <img src="../assets/news/foo.png" alt="..." loading="lazy" decoding="async" width="1600" height="900">
    </picture>
    <figcaption>SOURCE · ...</figcaption>
  </figure>
  ```

## 路徑慣例

- 文章頁在 `/posts/` 下，favicon / 導覽鏈結用 `../` 相對路徑
- 開發時雙擊 .html 打開（file://）也能看到完整樣式
- 上 Netlify 後絕對路徑 `/posts/` 依然有效

## 品牌規範（v2.0 · mono brutalist）

- 色系：純 black + 純 white + light gray `#F2F2F2`，完全 monochrome
- 無 acid / 無 gold / 無任何彩色 — 強度靠 type / size / contrast
- 字體：Inter Tight (heavy) + Space Grotesk + Noto Sans TC，全 sans
- 調性：editorial / brutalist / editorial signal
