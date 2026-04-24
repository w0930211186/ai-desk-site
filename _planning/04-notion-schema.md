# Notion「AI DESK 編輯台」資料庫 schema 規格

> Rick 開權限後我照這份 schema 自己建。你只需要：(1) 在 Notion 建一個叫「AI DESK 編輯台」的空 page (2) 邀 Anthropic 的 Notion integration 進來 (3) 把 page 的 URL 丟給我。

---

## 資料庫基本設定

- **名稱**：`AI DESK 編輯台`
- **類型**：Database (full page)
- **位置**：你的 workspace 裡任何地方都可以（建議放一個叫「AI DESK」的 parent page 下面）

---

## 完整欄位定義（共 18 欄）

| # | 欄位名 | 類型 | 必填 | 範例 / 備註 |
|---|---|---|---|---|
| 01 | **Title** | Title | Y | `2026/04/24 · AI 大事` — 每一列唯一識別 |
| 02 | **Status** | Select | Y | 8 個選項見下方 |
| 03 | **Category** | Select | Y | `daily` / `news` / `weekly` / `meta` |
| 04 | **Edition Num** | Number | Y | 自動從 01 開始遞增 |
| 05 | **Slug** | Rich text | Y | `2026-04-24-ai-daily-openai-price-cut`（ascii only） |
| 06 | **Publish Date** | Date | Y | 含時間 `2026-04-24 07:00 CST` |
| 07 | **Summary** | Rich text | Y | 140-160 字 · meta description / og 共用 |
| 08 | **Body** | Rich text / Page content | Y | 文章主體（可以用 Notion 的 block 編輯） |
| 09 | **Tags** | Multi-select | N | 自由加 · 先建 10 個預設 tag |
| 10 | **Sources** | URL[] (rich text 多行) | Y | 每行一條 URL · daily 必 ≥ 3 / news 必 ≥ 2 |
| 11 | **Warning Banner** | Select | N | `none` / `correction` / `wip` |
| 12 | **Prev Slug** | Rich text | N | sync 自動填 |
| 13 | **Next Slug** | Rich text | N | sync 自動填 |
| 14 | **Site URL** | URL | N | sync 完自動填 |
| 15 | **IG Approved** | Checkbox | N | Rick 手動勾 |
| 16 | **IG Media ID** | Rich text | N | ig-ship 自動回寫 |
| 17 | **IG Caption** | Rich text | N | render 自動填 / Rick 可改 |
| 18 | **Notes** | Rich text | N | 備註 · Rick 自由寫 |

---

## Status 生命週期（8 個選項 · 顏色由淺到深）

```
inbox       ← scout 剛抓進來還沒動
draft       ← draft skill 寫好草稿了 等 Rick 看
ready       ← Rick 看完 OK 了 準備 ship
shipping    ← ship skill 正在跑三色燈檢查
blocked     ← 三色燈紅 → 卡住 等 Rick 修
shipped     ← 官網已上線
ig-shipped  ← IG 也發了
skipped     ← 今天不發 跳過
archived    ← 歷史
```

轉換圖：
```
inbox ──(draft skill)──▶ draft
                            │
                            │ Rick 切
                            ▼
                          ready ──(ship skill)──▶ shipping
                            ▲                         │
                            │                         ├─🔴 blocked ─(Rick 修)─▶ ready
                            │                         │
                            │                         ├─🟢 shipped
                            │                         │
                            └── (Rick 手動退)        ▼
                                                  ig-shipped (或 skipped)
                                                     │
                                                     ▼
                                                  archived (30 天後自動)
```

---

## Category Select 的顏色建議（視覺好認）

| Category | 顏色 | 意義 |
|---|---|---|
| `daily` | Blue | 每天的 AI 大事 · 最大量 |
| `news` | Purple | 深度新聞 · 週二五 |
| `weekly` | Orange | 一週回顧 · 週日 |
| `meta` | Gray | 站務 / 發刊詞 / 聲明 |

---

## 預設 Tags（先建這 10 個 · 之後自由加）

`OpenAI` `Anthropic` `Google` `Meta` `Nvidia` `開源模型` `工具` `監理/政策` `KOL` `創業`

---

## Views（建四個）

### View 1 · Inbox（scout 的收件匣）
- Filter: Status = `inbox` OR `draft`
- Sort: Edition Num desc
- Rick 每天早上 06:00 看這個

### View 2 · 今日待辦（Rick 的工作區）
- Filter: Status = `draft` OR `ready` OR `blocked`
- Sort: Publish Date asc
- Rick 的主戰場

### View 3 · 已上線（官網對照）
- Filter: Status = `shipped` OR `ig-shipped`
- Sort: Publish Date desc
- 用來 double-check 官網內容

### View 4 · 封存
- Filter: Status = `archived`
- Sort: Publish Date desc
- 歷史查閱用

---

## Body 欄位怎麼用（重要）

Notion 的 Rich text 在 API 取出來會是他們自己的 block 結構。我會在 sync skill 裡寫一個 `notion_blocks → html` 的轉換器。

支援的 block 類型：
- `heading_2` → `<h2><span class="num">N°XX</span>Heading</h2>`
- `heading_3` → `<h3>`
- `paragraph` → `<p>`
- `bulleted_list_item` → `<ul><li>`（渲染成 `◆` bullets）
- `numbered_list_item` → `<ol><li>`
- `quote` → `<blockquote>`
- `code` → `<pre><code>`
- `image` → `<figure><img>`（用 Notion 的 public URL）
- `divider` → `<hr>`

**rich text inline 支援**：
- bold → `<strong>`
- italic → `<em>`（這在 AI DESK 是 outline 效果不是斜體）
- code → `<code>`
- link → `<a href>`

**不支援**（skill 會 skip）：
- toggle, callout, embed, bookmark, file, audio

---

## 權限設定（Rick 要做的）

1. Notion 右上 → Settings & members → Integrations
2. 找「Anthropic Claude」或「AI DESK Automation」（如果要另建的話）
3. 授權進入你的 workspace
4. 到「AI DESK 編輯台」這個 page → 右上角「···」→ Add connections → 選 integration
5. 把 page 的 URL 丟給我（長這樣 `https://notion.so/xxxxx-xxxxxxxxxxx`）

做完後我跑一個測試：
- 讀取：讀出 database schema OK
- 寫入：建一個 test row 看能不能進去 OK
- 兩邊 OK 了 → 我建正式的 18 個欄位 + 4 個 views

---

## 一個常見問題先講

> Notion 免費版能用 integration 嗎？

可以。個人版免費。但如果你要多人協作編輯 / 加權限控制 建議升級 Plus（每月 $10）。現階段個人版就夠了。

---

## 備份策略

Notion 本身有 30 天 version history。另外我在 sync skill 每次發布時會把 markdown 備份到 `/outputs/ai-desk-archive/YYYY-MM-DD/` — 連 Notion 掛了我們 local 還有拷貝。

---

## 這份規格動到時更新

schema 有任何改變（加欄位 / 改 Status 選項）都更新這份檔案 + 在 `CHANGELOG` section 記日期。
