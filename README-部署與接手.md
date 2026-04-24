# AI DESK — 部署與接手說明

> 開站日期：2026-04-24
> 編輯台：AI DESK（獨立品牌 無個人署名）
> 版本：v2.0（mono brutalist · 參照 regisgrumberg.com · 圓形入場 · 傾斜卡片 · 純黑白）

---

## 一、這包是什麼

AI DESK 是一個**獨立的 AI 編輯台** 自己一套視覺 自己一條聲音線 自己一個立場
v2.0 從「editorial + acid accent」重建為「mono brutalist editorial」風格
參考：`https://www.regisgrumberg.com/`

預計跑在 Netlify 假設網址 `ai-desk.netlify.app`（實際網址以 Netlify 分配為準）

---

## 二、檔案結構

```
ai-desk-site/
├── index.html                              # 首頁（圓形入場 · 傾斜卡片 · 大浮水印 · 淺灰 slab）
├── about.html                              # 立場書（黑白交替 slab · rules grid · honest zone）
├── 404.html                                # 錯誤頁（巨大 404 浮水印）
├── netlify.toml                            # Netlify 設定（快取 / redirect / headers）
├── robots.txt                              # 爬蟲規則
├── sitemap.xml                             # Google 索引（開站時 4 條）
├── assets/
│   └── favicon.svg                         # 品牌 icon（黑白旋轉菱形 — brand-dot）
└── posts/
    ├── index.html                          # 全部刊文索引（tag filter · 月份分組）
    ├── _template.html                      # 文章模板（給未來 skill 用 · 含 placeholder）
    └── 2026-04-24-ai-desk-opening.html     # 發刊詞
```

---

## 三、架構：inline CSS（無外部 stylesheet）

每個 HTML 檔案都把 CSS 寫在 `<style>` 標籤裡 **沒有共用的 style.css**

理由：
- 雙擊 `.html` 用 `file://` 協定打開 就能看到完整設計 不用起 server
- Netlify 部署一樣 OK HTML + gzip 每頁 ~18-30KB first-paint 不用等
- 未來 `ai-journal-sync` skill 直接照 `posts/_template.html` 生檔 所有樣式已內嵌 一個檔案寫完就發

### 路徑規範

| 檔案位置 | 資源引用 |
|---|---|
| 根目錄 (`index.html` / `about.html`) | `assets/favicon.svg` / `posts/...`（相對） |
| `posts/` 下 | `../assets/favicon.svg` / `../index.html` / `../about.html` |
| 同層 `posts/` | `index.html` / `2026-04-24-...html` |
| `404.html` | 用絕對路徑 `/` `/posts/` `/about.html`（Netlify fallback） |

---

## 四、五分鐘部署到 Netlify

### 方案 A · Netlify Drop（最快、零設定）

1. 進 <https://app.netlify.com/drop>
2. 把 `ai-desk-site/` 整個資料夾拖進去
3. Netlify 會分配一個隨機 URL 例如 `https://fancy-cat-abc123.netlify.app`
4. 進 **Site settings → Domain management** 改 Site name 改成 `ai-desk`
5. 最終網址會是 `https://ai-desk.netlify.app`

### 方案 B · Git 連動（推薦 未來自動化要用）

1. 本機建一個 git repo 例如 `~/ai-desk-site/`
2. 把 `ai-desk-site/` 的內容搬進去
3. 推到 GitHub 私人 repo
4. 進 Netlify → **Add new site → Import from Git**
5. 選那個 repo Build settings 留空（純靜態）Publish directory 設 `.`
6. Deploy 設好之後每次 push 就自動部署

→ 未來 `ai-journal-sync` skill 的做法是 直接寫檔案進這個 repo git push 自動觸發 Netlify 重建

---

## 五、給未來 `ai-journal-sync` skill 的注入規範

**Skill 的工作流：**

1. `notion-search` 抓 Notion AI 編輯台資料庫最新文章
2. 每篇文章：
   - 讀取 `posts/_template.html` 當骨架（CSS 已內嵌 無需外掛）
   - 替換所有 `{{...}}` placeholder
   - 寫到 `posts/<slug>.html`
3. 重建 `posts/index.html` 的 `<!-- POSTS-INJECTION-START -->` 區塊
4. 重建首頁 `index.html` 的 `<!-- FEED-INJECTION-START -->` 區塊（最新 6 則散落卡片）
5. 重建 `sitemap.xml`
6. git push → Netlify 自動重建

### Placeholder 速查（`posts/_template.html` 裡已寫註解）

| Placeholder | 範例 |
|---|---|
| `{{TITLE}}` | `Claude Opus 4.6 實戰三天心得` |
| `{{TITLE_SHORT}}` | `Opus 4.6 三天心得` |
| `{{SUMMARY}}` | `跟 Sonnet 比快了多少 錯了多少 ...`（140-160 字） |
| `{{SLUG}}` | `2026-04-25-claude-opus-4-6-test` |
| `{{DATE_ISO}}` | `2026-04-25T07:00:00+08:00` |
| `{{DATE_DISPLAY}}` | `2026 · 04 · 25` |
| `{{DAY}}` | `SAT` |
| `{{EDITION_NUM}}` | `02` |
| `{{CATEGORY}}` | `tools` (news / tools / intel / meta 四選一) |
| `{{CATEGORY_LABEL}}` | `Tools · 工具` |
| `{{TAG_CHIPS}}` | `<span class="tag">Tools · 工具</span><span class="tag mute">Claude</span>` |
| `{{WARNING_BANNER}}` | 空字串 或 `<div class="warning">...</div>` |
| `{{BODY_HTML}}` | semantic HTML：`<h2><span class="num">N°01</span>XXX</h2>`、`<p>`、`<blockquote>`、`<ul>` 等 |

### 文章內 HTML 慣例

- `<h2>` 可選加 `<span class="num">N°01</span>` 產生編號標籤（mono 字型 灰色）
- `<em>` 不是斜體 是 outline 效果（字變透明 外描邊）用於標題關鍵字
- `<ul>` 自動 ◆ bullet（實心菱形）
- `<ol>` 自動 01/02/03 編號（mono 字型）
- `<blockquote>` 全寬橫線 + ❝ 開口 + 全大寫 用於金句
- `<img>` 寬度自動 100% 配 faint 邊
- inline `<code>` / `<pre>` 都有 token 樣式 半透明白底

### 首頁 feed 注入規格（v2.0 散落卡片）

首頁 `index.html` 裡 `<!-- FEED-INJECTION-START -->` 會被覆寫
最多 6 張卡片 每張指定 class `c1` ~ `c6` 控制散落位置（已在 CSS 中 pre-defined）
每張卡片 HTML 格式：

```html
<a href="posts/{slug}.html" class="journal-card c{n} reveal">
  <div class="card-meta"><span>N°{edition}</span><span>{YYYY · MM · DD}</span></div>
  <h3>{title}</h3>
  <p>{summary 前 80 字}</p>
  <div class="card-foot"><span>{category_label}</span><span class="arrow">→</span></div>
</a>
```

未發布的坑位用 `<div class="journal-card ghost c{n} reveal">`（黑底白框 · 描邊版）

### 列表頁 `posts/index.html` 注入規格

每個 `.month-block` 下是 `.post-row`：

```html
<a href="{slug}.html" class="post-row" data-tags="{category}">
  <div class="date">{MM · DD · DAY}<br>N°{edition}</div>
  <div class="info">
    <h3>{title}</h3>
    <p class="excerpt">{summary 前 80 字}</p>
    <div class="inline-tags"><span>{category_label}</span></div>
  </div>
  <div class="arrow">→</div>
</a>
```

---

## 六、編輯聲音 checklist（給 skill 用）

這些是 AI DESK 的底線 自動化也不能破

- [x] 繁體中文為主 技術名詞留英文（Anthropic / Claude / MCP / agent）
- [x] 中文字之間用**空格**不用全形標點（。，、；：都改空格）
- [x] 不 AI 化 不寫「總而言之」「讓我們一起」「值得關注」這種套話
- [x] 帶江湖味 可以用「這事兒」「我實話講」「別裝」等口語
- [x] 金句用 `<blockquote>` 包起來 每篇至少一句 寫成全大寫口號感
- [x] 誠實區 · 不 hype 不唱衰 給數字跟脈絡 不給情緒
- [x] 每篇結尾署名：`— AI DESK · 編輯台 / Edition N°XX · YYYY · MM · DD · Taipei`
- [x] 標題可用 `<em>` 做關鍵字 outline 強調 但一篇最多兩處
- [x] **禁止**：提及任何姊妹品牌 / 母公司 / 個人身份

---

## 七、視覺系統速查（CSS tokens · v2.0）

每個 HTML 內嵌 `<style>` 都有完整這組 token：

```css
--bg:       #000000    /* 主背景 純黑 */
--fg:       #FFFFFF    /* 主前景 純白 */
--panel:    #F2F2F2    /* 淺灰 slab 區塊 */
--panel-fg: #0A0A0A    /* 淺灰區內文字 */
--mute:     #8A8A8A    /* 次要字 / meta */
--mute-2:   #5A5A5A    /* 更淡字 */
--line:     rgba(255, 255, 255, 0.14)   /* 黑底 hairline */
--line-dark:rgba(0, 0, 0, 0.14)         /* 灰底 hairline */
```

字體 stack（全 sans · 無襯線）：

```css
--f-display: 'Inter Tight', 'Noto Sans TC', -apple-system, sans-serif;
  /* 可變粗細 300-900 · 大標用 900 · 小字用 500/600 */
--f-sans:    'Space Grotesk', 'Noto Sans TC', sans-serif;
  /* 標籤 / UI / 導覽 */
--f-body:    'Noto Sans TC', 'Inter Tight', sans-serif;
  /* 中文內文主力 */
--f-mono:    'JetBrains Mono', 'SF Mono', Menlo, monospace;
  /* date / code / 期數 */
```

### v2.0 設計簽名（mono brutalist）

1. **巨型浮水印** — 每個主要區塊都有一組 transparent + stroke 1px 的超大區段名（`AI DESK` / `JOURNAL` / `ABOUT` / `EDITORIAL` / `404`）
2. **圓形 rotating text** — 首頁 hero 用 SVG textPath 繞 170px 圓 26s 旋轉一圈 中間是圓形 ENTER 按鈕
3. **傾斜散落卡片** — 首頁 journal 區用 `rotate(-5deg ~ 6deg)` + absolute position 做 3D 感 hover 自動回正上浮
4. **黑白交替 slab** — about 頁是 hero(黑) → slab(黑) → slab(灰) → slab(黑) → contact(灰) → footer(黑) 強對比節奏
5. **旋轉菱形 brand dot** — nav 上左邊那個黑方塊（`.diamond`）一直在轉 · 配合浮動裝飾菱形
6. **outline 字** — `<em>` 不是斜體 是 `color: transparent; -webkit-text-stroke: 1.5px currentColor` 的描邊效果
7. **超大 footer lockup** — 每頁 footer 都是 `clamp(4rem, 14vw, 16rem)` 的 `AI DESK` 巨字

排版節奏：
- Hero 大標 `clamp(3.5rem, 10vw, 9rem)` weight 900 · text-transform uppercase
- Section title `clamp(2rem, 4.4vw, 4rem)` weight 900
- H2 `clamp(1.8rem, 3.5vw, 2.6rem)` weight 900
- Body 17px line-height 1.9（中文閱讀最舒服區間）
- 文章 max-width 760px · 列表 / slab max-width 1400px

### v1.0 → v2.0 的變動點

| 層面 | v1.0 | v2.0 |
|---|---|---|
| 主背景 | `#0A0D14` 墨黑偏藍 | `#000000` 純黑 |
| 主色 | acid chartreuse `#D4FF4F` | 無 · 純 monochrome |
| 內文色 | `#EDEAE3` 紙白 | `#FFFFFF` 純白 |
| 字體 | Fraunces (襯線 + 斜體) | Inter Tight (無襯線 + 粗體) |
| 強調 | 金字 italic | outline 描邊字 |
| 節奏 | 章節式長捲動 | 黑白交替 slab + 傾斜散落卡片 |
| 入場 | direct hero | 圓形 rotating text + ENTER |
| 清單 | 文章列表條目 | 散落 3D 傾斜卡片（首頁） + 條目（列表頁） |
| 調性 | editorial 襯線感 | brutalist sans · 強對比 |

---

## 八、下一步（v2.1 待辦）

1. 決定網址（`ai-desk.netlify.app` / `ai-column.netlify.app` / 買獨立域名）
2. **IG 誘餌貼 + 機器人 DM funnel**（待規劃）：
   - CT 圖文（carousel）埋關鍵字 CTA 例「留言 GPT 領筆記」
   - IG Messenger API / ManyChat 抓留言自動 DM
   - DM 話術先要求「追蹤才發連結」
   - 連結指向 Notion 公開頁（筆記內容）
   - 需要：Meta Graph API 權限 + Notion public share link + 規劃 CTA skill
3. 寫 `ai-journal-sync` skill（Notion → 站點的自動供稿管線）
4. 寫 `ai-column-scout` skill（掃新聞 + 對手 + 工具）
5. 寫 `ai-column-draft` skill（scout 情報 → 草稿到 Notion）
6. 寫 `ai-column-ship` skill（三色燈 + 塗銷 + 通知）

---

## 九、驗收結果（v2.0）

- 所有 6 頁 HTTP `200` 通過 本地 `http://127.0.0.1:8765`
- 所有 6 頁內嵌 inline `<style>` 都使用 v2.0 mono token（`--bg #000` / `--fg #FFF`）
- 零 `--acid` / `--gold` / `--cream` 殘留（HTML / SVG 完全 clean）
- 零 BEXS / Rick Bowen 字串
- 首頁含 6 組浮水印 · about 2 組 · 404 2 組 · journal 列表頁 2 組（視覺簽名落實）
- favicon 從 acid 圓點改成純黑白旋轉菱形

Rick 你現在應該：

1. 打開 `ai-desk-site/` 目錄看整包東西
2. 雙擊 `index.html` 在瀏覽器預覽 應該能看到：
   - 圓形 rotating text + ENTER 按鈕（hero）
   - 幾個浮動小菱形（hero 四角）
   - 散落的傾斜卡片（journal 區 · 6 張 1 實 5 ghost）
   - 淺灰 slab + 大字 lede（about 區）
   - 黑底 manifesto（全大寫口號）
   - 巨型 `AI DESK` footer lockup（淺灰底）
3. 滿意就丟 Netlify Drop 上線 不滿意回來講哪裡要改
4. 講下一步：IG funnel 架構怎麼搭 / 四個 skill 哪個先寫

有任何視覺 / 口吻 / 結構要調整的 直接說

— *本文件 v2.0 由 Claude 於 2026-04-24 為 mono brutalist 重建後撰寫*
