# AI DESK 自動化管線 — 四個 skill 各自在幹嘛

> 這份是給 Rick 的記憶備份。一個 skill 就是一個「獨立作業的小員工」，合起來是整條編輯部。看完這頁你就知道 skill 名字 → 打開時要做什麼事。

---

## 管線總圖（想像成一條輸送帶）

```
[ 外面的世界 ]
      │
      ▼
┌────────────────┐     (每天早上 05:30 CST 跑一次)
│ ai-column-scout│  掃 RSS / KOL / GitHub / HN / arxiv 等 → 挑 3-5 條 candidate → 寫進 Notion Inbox
└────────┬───────┘
         │
         ▼
┌────────────────┐     (scout 跑完 直接觸發 · 約 06:00 CST)
│ ai-column-draft│  把 candidate 寫成完整草稿（按 AI DESK 聲音）→ 更新 Notion Draft
└────────┬───────┘
         │
         ▼
     [ Rick 看一下 把 Status 改成 ready ]  ← 人工守門閥（重要）
         │
         ▼
┌────────────────┐     (監聽 status=ready 觸發 · 07:00 整點前)
│ ai-column-ship │  三色燈檢查（語法 / 連結 / AI 聲明）→ 通過 → 觸發 sync
└────────┬───────┘
         │
         ▼
┌────────────────┐     (07:00 CST 整點)
│ai-journal-sync │  Notion → _template.html → /posts/YYYY-MM-DD.html → git push → Netlify 自動 build
└────────┬───────┘
         │
         ▼
   [ 官網更新 ]
         │
         ▼
┌────────────────┐     (sync 完成後觸發)
│ ai-ig-render   │  吃文章 → 產 5-8 張 1080×1350 carousel PNG → 上傳到 Notion 預覽
└────────┬───────┘
         │
         ▼
   [ Rick 手機 DM 確認 OK ]  ← 第二道人工閥（可選）
         │
         ▼
┌────────────────┐     (批准後觸發)
│ ai-ig-ship     │  IG Graph API container → publish → 寫回 Notion「IG 已發」
└────────┬───────┘
         │
         ▼
   [ IG 上線 · 讀者留言關鍵字 ]
         │
         ▼
┌────────────────┐     (webhook 觸發)
│ ai-dm-funnel   │  關鍵字觸發 DM → follow-first gate → 送出 Notion 公開連結
└────────────────┘
```

核心四個 skill 是底下這四個。IG 那兩個 + DM 那個是第二波。

---

## skill #1 — `ai-column-scout`

**一句話定義**　把外面世界發生的 AI 大事掃回來變成 Notion inbox。

**什麼時候跑**　每天 05:30 CST（定時）；也可以 Rick 手動「掃一下情報」觸發。

**input**　什麼都不吃。內建一份資訊源清單：
- RSS：TechCrunch AI / The Information / Stratechery / Platformer / Import AI
- KOL：預先追蹤的 Twitter/X 帳號清單（OpenAI員工 / Anthropic員工 / AI lab founder / dev community voices）
- GitHub Trending（language=python, topic=ai / llm / agent）
- Hacker News 前 30 條 filter AI/LLM 關鍵字
- arxiv cs.AI / cs.CL 當日新 submit

**做什麼**
1. 抓今日所有 hit，去重
2. 每條打 relevance 分（有多少獨立源提、是否首發、是否結構性變化）
3. 按分數排序取 top 5，寫進 Notion「AI DESK 編輯台」database，status=inbox
4. 每條附：來源連結、摘要 50 字、tag、relevance 分數、抓取時間

**output**　Notion inbox 裡 3-5 個 candidate row。

**失敗怎麼辦**　任何一個源抓不到 → 跳過繼續、寫 log；全部抓不到 → draft Gmail 通知 Rick。

---

## skill #2 — `ai-column-draft`

**一句話定義**　把 inbox 的 candidate 寫成完整文章草稿。

**什麼時候跑**　scout 完自動觸發（約 06:00 CST）；也可以手動指定某個 candidate id 觸發。

**input**　Notion 某一 row，status=inbox 的 candidate。

**做什麼**
1. 讀 candidate 的來源連結（跑 web_fetch 抓全文）
2. 按照 AI DESK 聲音規則寫：
   - **Daily 大事**格式：3-5 條 bullet + 每條 50-80 字 + 每條附原始 link
   - **News 深度**格式：一件事 1200-2000 字 前因後果拆清楚
   - **Weekly 回顧**格式：時間線排列 + 重要度星號 + 每條附連結
3. 填 `_template.html` 的 placeholder：{{TITLE}} {{SUMMARY}} {{BODY_HTML}} {{CATEGORY}} {{TAG_CHIPS}} 等
4. 把完整草稿寫回 Notion，status=draft
5. Gmail 通知 Rick「今日 draft ready 進來看」

**output**　Notion row 狀態 inbox → draft + body 欄位填好。

**聲音規則（重要）**
- Matter-of-fact、不吹不捧
- 中文為主 英文術語夾雜
- 禁用「爆、猛、神、厲害」這類情緒詞
- 禁用「你必須知道 / 一次看懂 / 小編」這類農場調
- 每條都要有源連結（daily 必加，news 至少 2 個 source）
- 可以有 `<em>` outline 強調但不濫用
- 金句用 blockquote 但不要每篇都硬塞

---

## skill #3 — `ai-column-ship`

**一句話定義**　人工守門後的最後守門閥 + 觸發 sync。

**什麼時候跑**　Rick 在 Notion 把某 row 的 Status 改成 `ready` 時自動觸發；也可以 Rick 說「ship 今天的」觸發。

**input**　Notion row，status=ready。

**做什麼（三色燈檢查）**
1. **紅燈（blocker）**
   - 有沒有填 Title / Slug / Body
   - Slug 是否符合 `YYYY-MM-DD-xxx` 格式
   - Body 有沒有危險字（未填的 placeholder / 測試殘留）
2. **黃燈（warning）**
   - 所有外部連結 HTTP 檢查一遍，404 回報
   - 錯字偵測（常見混淆詞）
   - 關鍵字密度（避免同詞重複太多）
3. **綠燈（shippable）**
   - AI 聲明段落有沒有（本文 AI 參與度）
   - 來源 ≥ 2 個（news 類強制）
   - Tag 至少 1 個
   
**紅燈**　卡住、status 改回 `draft`、Gmail 通知 Rick 為什麼卡。
**黃燈**　通過但 draft 一封給 Rick 讓他確認。
**綠燈**　status → `ready-to-ship` → 觸發 ai-journal-sync。

**output**　status 更新 + 通過/失敗事件。

---

## skill #4 — `ai-journal-sync`

**一句話定義**　Notion 已 ship 的文章 → 官網 → git push → Netlify 上線。

**什麼時候跑**　ai-column-ship 綠燈後自動觸發；也可以 Rick 說「同步官網」手動觸發。

**input**　Notion status=`ready-to-ship` 的 row。

**做什麼**
1. 從 Notion 抓完整內容（Title / Slug / Summary / Body / Category / Tags / Date / Edition Num）
2. 讀 `/posts/_template.html`
3. 把 placeholder 替換成實際值
4. 寫到 `/posts/{SLUG}.html`
5. 重新組 `/posts/index.html` 的 `<!-- POSTS-INJECTION-START -->` 區塊：
   - 按 YYYY-MM 分組
   - 最新的月份在最上面
6. 更新 `/index.html` 的 `<!-- FEED-INJECTION-START -->` 區塊：
   - 拿最新 6 篇出來
   - 最新那篇放 c1 卡（非 ghost）
   - 其他 5 篇放 c2-c6
7. 更新 `/sitemap.xml` 加入新 URL
8. git add / commit / push 到 GitHub
9. Netlify 收到 push 自己 rebuild
10. 寫回 Notion status=`shipped` + 官網 URL
11. 觸發 ai-ig-render（第二波）

**output**　一個上線的 /posts/ URL + Notion row 已蓋章。

**失敗怎麼辦**
- Notion API fail → 重試 3 次 → Gmail 通知
- git push fail → 保留 local changes → Gmail 通知
- 任何 step fail → status 回退到 `ready` + 完整 error log

---

## 第二波（IG 自動化 · 還沒動）

| skill | 做什麼 | 觸發 |
|---|---|---|
| `ai-ig-render` | 讀文章 → 按 Rick 給的 carousel 模板 → 產 5-8 張 PNG | sync 完成後 |
| `ai-ig-ship` | Graph API container upload → publish → 寫回 Notion | Rick DM 確認後 |
| `ai-dm-funnel` | webhook 接 IG 留言關鍵字 → DM 話術 → Notion 連結 | 即時 |

這三個等前四個跑通了再開工。

---

## 為什麼這樣切（架構決策）

**為什麼不是一個大 skill 一次做完？**　因為每一段都可能失敗。切開才能單獨重跑 / 單獨 debug / 單獨替換。

**為什麼保留兩道人工閥？**　第一道（Rick 看 draft）守品質；第二道（Rick 看 IG carousel）守形象。自動化是為了省時間，不是為了讓 Rick 失控。

**為什麼用 Notion 當中樞？**　因為 Rick 想在手機上滑、改、批准。Notion 是目前最順手的 workflow 容器。官網只是 output，不是 source of truth。

**為什麼 skill 之間用 status 欄位當通訊？**　簡單、可觀測、手動能 override。比 event bus / queue 適合這個小規模。
