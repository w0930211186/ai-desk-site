---
name: ai-column-ship
description: 當 Rick 把 Notion row 的 Status 切成 ready 時 觸發三色燈檢查（事實核對 / 來源查驗 / 格式驗證 / 禁用字 / SEO 完整度）— 綠燈 → 自動觸發 ai-journal-sync 發布官網；紅燈 → 卡住回寫 blocker → email Rick。當 Rick 說「發布 / ship / 過三色燈 / 檢查可以發了嗎 / 過稿 / 上線檢查 / 準備上刊」等類似指令時手動觸發 即使沒明確說「用 skill」。
---

# ai-column-ship

獨立 AI 編輯台的三色燈守門員。在 `ai-journal-sync` 真正發布官網之前 做最後一道品質檢查。失敗就卡住 不讓有毛病的稿子上線。

## 觸發詞

中文：發布檢查、上刊檢查、過三色燈、ship、準備上線、發了嗎、過稿、準備發布

English: ship check, tri-color gate, pre-publish lint, ready to ship

## 觸發方式

1. **自動**：Notion webhook 偵測 Status `draft → ready`（或 `blocked → ready`）自動跑
2. **手動**：Rick 在聊天說「過三色燈」「ship 一下」
3. **排程**：每日 06:55 掃所有 Status = `ready` 的 row 批次跑

## 依賴

**環境變數**
```
NOTION_TOKEN=secret_xxxx
NOTION_DATABASE_ID=xxxx
ANTHROPIC_API_KEY=sk-ant-xxxx
GMAIL_DRAFT=on
```

## 三色燈規格

### 🔴 紅燈 blocker（任何一條中就停）

| 檢查項 | 規則 | fail 動作 |
|---|---|---|
| R1 · 來源缺失 | daily ≥ 3 個 source URL / news ≥ 2 個 | Status 退 `blocked` + email |
| R2 · 來源無法訪問 | 對每個 source URL HEAD check HTTP < 400 | 同上 |
| R3 · Title 空 / 超長 | 10-80 字之間 | 同上 |
| R4 · Summary 空 / 字數不對 | 140-160 字 | 同上 |
| R5 · Body 空 / 結構異常 | 至少 1 個 H2 + 3 個 paragraph | 同上 |
| R6 · Publish Date 過去 | 已過的時間不能發 | 同上 |
| R7 · Slug 已存在於官網 | 避免覆蓋歷史文章 | 同上 |
| R8 · 禁用字命中 | voice.md 禁用字 | 同上 |

### 🟡 黃燈 warning（繼續發 但 email 提醒）

| 檢查項 | 規則 | 繼續 but notify |
|---|---|---|
| Y1 · Tag < 2 個 | 建議 2-5 個 | email Rick「標籤太少影響 SEO」 |
| Y2 · 無 image block | Body 裡沒圖 | email「建議加張圖」 |
| Y3 · H3 只有 1 個 | 結構太扁 | email 建議再分段 |
| Y4 · Summary 與 Body 首段重複率 > 70% | 懶 | email 建議重寫 summary |
| Y5 · 同 tag 24h 內已發過 | 重複主題 | email 提醒避免洗版 |
| Y6 · Edition Num 不連續 | 可能跳號 | email 提醒 |

### 🟢 綠燈（全部過 自動進發布）

自動：
1. 寫回 Notion `Notes` 欄位：三色燈報告 + 時間戳
2. Status 保持 `ready`
3. 觸發 `ai-journal-sync` skill
4. sync 完自己會改 Status → `shipped`

## 執行流程

### 1. 取 Notion row 全內容
Fetch page properties + all blocks。

### 2. 跑紅燈 R1-R8
任何一條 fail → 組 blocker email → 停。

### 3. 跑黃燈 Y1-Y6
收集所有 warnings 進 list（不停止）。

### 4. 產三色燈報告
寫回 Notion Notes 欄位：
```
— 三色燈 · YYYY-MM-DD HH:mm —
🟢 過
R1 來源 3 條 ✓
R2 來源全部 200 ✓
R3 Title 32 字 ✓
R4 Summary 148 字 ✓
R5 Body 2 H2 / 6 p ✓
R6 Publish 2026-04-24 07:00 ✓
R7 Slug unique ✓
R8 禁用字 清 ✓

Warnings: 無

下一步：觸發 ai-journal-sync
```

或紅燈：
```
— 三色燈 · YYYY-MM-DD HH:mm —
🔴 卡住 Rick 要處理

R2 來源無法訪問：
  - https://example.com/foo (404)

修好後把 Status 從 blocked 改回 ready 會自動重跑
```

### 5. 綠燈 → 觸發 sync
直接呼叫 `ai-journal-sync`（或寫一個 `trigger` 檔案在 Notion Notes 讓 sync poll）。

### 6. 紅燈 → email draft

```
Subject: [AI DESK · 🔴] ship · <title> 卡在三色燈 等你修

Rick

今日稿子 "<title>" 三色燈沒過 卡在 blocked

— 紅燈 —
<list of failures>

— Rick 要做什麼 —
[ ] 打開 Notion: <url>
[ ] 按上面清單修
[ ] Status 從 blocked 改回 ready → 自動重跑

黃燈（不擋但建議看）:
<list of warnings or "無">
```

## 事實核對（可選 v2 加）

未來版本加一個 `fact-check` 步驟：
- 撈 Body 裡所有數字 / 人名 / 公司名 / 日期
- 用 Claude + web_search 驗證
- 任何懷疑進黃燈

**現階段跳過** — 只信 draft skill 寫出來的東西 + Rick 的肉眼。

## 錯誤處理

| 情境 | 行為 |
|---|---|
| Notion API timeout | 3 次重試 → 🔴 email + Status 不動 |
| 一個 source URL 時好時壞 | 重試 3 次 都失敗才紅 |
| `ai-journal-sync` 觸發後失敗 | 不回頭改 Status（由 sync 自己處理） |
| Webhook 太頻繁 debounce | 同一個 row 30 秒內多次 trigger 只跑一次 |

## 測試

```bash
python scripts/ship.py --page-id=<notion-page-id>
# 對單一 row 跑完整檢查

python scripts/ship.py --dry-run --page-id=<id>
# 不真的 trigger sync 只 print 報告

python scripts/ship.py --simulate-red R2
# 模擬某個紅燈 看通知有沒有寫對
```

## 冪等性

同一個 page 跑多次：
- Notes 欄位每次覆寫（不累積）
- 不會重複觸發 sync（如果已經是 shipped 直接 skip）
- Webhook debounce 30 秒

## 實作結構

```
skills/ai-column-ship/
  ├── SKILL.md
  ├── scripts/
  │   ├── ship.py           (主入口)
  │   ├── checks/
  │   │   ├── red.py        (R1-R8)
  │   │   ├── yellow.py     (Y1-Y6)
  │   │   └── sources.py    (URL HEAD check)
  │   ├── reporter.py       (三色燈報告產生)
  │   └── trigger.py        (呼叫 sync)
  └── tests/
      ├── test_red.py
      ├── test_yellow.py
      └── fixtures/
          ├── good_row.json
          └── bad_row.json
```

## 三色燈 SLA

- 綠燈全過 → 觸發 sync 在 60 秒內
- 紅燈卡住 → email draft 在 120 秒內
- 黃燈警告 email → 跟綠燈一起出（不另外一封）

## 為什麼這道關口要獨立

- 把「檢查」和「發布」解耦 → 檢查 fail 時發布邏輯完全不動
- 讓 Rick 看 `blocked` status 就知道要做什麼 不用翻 log
- 未來加事實核對 / AI 二審只要改 ship 不動 sync
- 每次檢查都寫 Notes → 有歷史紀錄可查

## 未來擴充（v2+）

- [ ] v2 加 fact-check pass
- [ ] v2 加「同行稿件比對」— 看對手媒體有沒有發過同主題
- [ ] v3 加 SEO 分數檢查（keyword density / meta length）
- [ ] v3 加圖片壓縮 / alt text 齊全檢查
