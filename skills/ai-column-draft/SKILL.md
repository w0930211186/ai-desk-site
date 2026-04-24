---
name: ai-column-draft
description: 把 Notion inbox 裡 scout 抓回來的 candidate 寫成 AI DESK 風格的草稿 — 每天 05:45 自動接在 scout 後面跑。當 Rick 說「寫今天的稿 / 生草稿 / draft 一下 / 改寫成 AI DESK 語氣 / 把 inbox 的東西寫起來 / polish inbox / 寫今日 AI 大事」等類似指令時觸發 即使沒明確說「用 skill」。產出 Status=draft 的 Notion row 等 Rick 06:00 審稿。
---

# ai-column-draft

獨立 AI 編輯台的寫手。從 inbox 撈 candidate → 寫成 AI DESK 風格的雙語稿 → Status=draft → email draft 通知 Rick。

## 觸發詞

中文：寫草稿、draft 一下、生稿、寫今日 AI、改寫語氣、polish inbox、把 inbox 寫起來、寫今天的專欄

English: draft article, write post, polish candidates, compose column, ai desk voice rewrite

## 依賴

**環境變數**
```
NOTION_TOKEN=secret_xxxx
NOTION_DATABASE_ID=xxxx
ANTHROPIC_API_KEY=sk-ant-xxxx     # draft 寫手用
GMAIL_DRAFT=on                     # 06:00 通知開關
```

**檔案依賴**
- `prompts/voice.md` — AI DESK 語氣手冊（tone / 字數 / 句長 / 禁用字）
- `prompts/daily.md` — Daily 大事專用 prompt
- `prompts/news.md` — News 深度專用 prompt
- `prompts/weekly.md` — Weekly 回顧專用 prompt

## 執行流程

### 1. 從 Notion inbox 撈 candidate
查詢：`Status = inbox` AND `建立時間 ≥ 今日 00:00`
分組：
- `Category = daily` → 取最高分 3-5 條 → 合成 1 篇 Daily
- `Category = news` (週二/五才有) → 取最高分 1 條 → 單篇 News 深度
- `Category = weekly` (週日) → 取最高分 10 條 → 合成 1 篇 Weekly

### 2. 對每個要產的稿子

#### 2a. 收集上下文
- 每條 candidate 的 title / source / score / 命中關鍵字
- 抓原文前 3000 字（如果是 RSS）或 HN 前 20 樓（如果是 HN）
- 撈同主題過去 30 天的 shipped 文章（避免重複寫）

#### 2b. 呼叫 Claude（Messages API）
```
system: <讀 prompts/voice.md + prompts/{category}.md>
messages: [
  { role: "user", content: "今日 candidate：\n<json dump of candidates>\n\n請依手冊寫一篇 {category} 稿" }
]
model: claude-sonnet-4-6
max_tokens: 4096
```

#### 2c. 產出要求
- Title: 雙語 `YYYY/MM/DD · <中文 headline>`
- Summary: 140-160 字（meta description 用）
- Body: markdown 格式 含 h2/h3/p/ul/ol/blockquote/code/hr
- Tags: 從命中關鍵字自動推斷 2-5 個
- Category: 帶入
- Edition Num: 自動 +1

### 3. Markdown → Notion blocks
用 `markdown_to_notion_blocks.py` 轉：
- `## heading` → heading_2
- `### heading` → heading_3
- `paragraph` → paragraph
- `- bullet` → bulleted_list_item
- `1. numbered` → numbered_list_item
- `> quote` → quote
- `` `code` `` → inline code
- `` ```lang ``` `` → code block
- `---` → divider

Inline：`**bold**` `*italic*` `[text](url)` `` `code` ``

### 4. 寫進 Notion
- 建立新 row：Status = `draft`
- 填入 Title / Summary / Body / Tags / Category / Edition Num / Publish Date (= 明早 07:00 CST)
- 原始 candidate row Status → `archived`（避免 inbox 堆積）

### 5. 06:00 email 通知 Rick
```
Subject: [AI DESK · 🟢] draft · 今日草稿已就緒 等你看

Rick 早安

今日 {category} 草稿已寫好進 Notion：
- 標題：{title}
- 字數：{body_word_count}
- 命中 tag：{tags}

Notion: https://notion.so/ai-desk/{page_id}

你要做：
1. 打開上面連結看一下
2. 順眼 → Status 切 "ready"（06:55 系統會自動三色燈檢查後發布）
3. 不順眼 → 直接 Notion 改字 或 Status 切 "skipped"

沒動的話 06:55 會卡住不發 你明天再來

— draft skill · 05:45 CST
```

### 6. 06:50 提醒（如果 Status 還是 draft）
```
Subject: [AI DESK · 🟡] draft · 還剩 5 分鐘 你還沒動

提醒一下 今天的 draft 還沒切 ready
06:55 系統會自動卡住不發
```

## Voice Rules（`prompts/voice.md` 大致內容）

### 硬規則
- 中文主體 英文補充專有名詞（OpenAI / Anthropic 不翻）
- 句子短 每句不超過 40 字
- 不用「其實」「就是」「然後」開句
- 不用 emoji（除了頂部的 🔸 分隔符）
- 不用「筆者認為」/「個人覺得」— 寫第二人稱或事實陳述
- 不自稱「小編」/「我們」
- 專有名詞第一次出現帶原文 `Anthropic（Claude 母公司）`

### 結構骨架
```
H2 N°XX <雙語 headline>
  → 前情（30 字 pin 住重點）
H3 發生了什麼
  → 事實 3 段
H3 為什麼重要
  → 解讀 2-3 段
H3 我們的判斷
  → 一句話 take + 下一步觀察什麼
---（分隔）
<下一個 H2>
```

### 禁用字清單
「震撼」「炸裂」「王炸」「神作」「顛覆」「不容錯過」「別走開」「看到最後」「必讀」
（這些是內容農場味 AI DESK 不走這路線）

### Daily 字數要求
- 3-5 條大事 每條 200-350 字
- 總長 1200-1800 字
- 1 分鐘看完的閱讀節奏 = 短段落 + 強 headline

### News 深度字數要求
- 1 條深度 2500-3500 字
- 6-8 個 H3 小節
- 一定要有「反方觀點」小節

### Weekly 回顧字數要求
- 7-10 條 aggregation 每條 150-250 字
- 總長 1800-2500 字
- 開頭有一段 300 字「本週一句話」

## 錯誤處理

| 情境 | 行為 |
|---|---|
| inbox 空 | 🟡 email「今天沒東西寫 Rick 看看是 scout 出問題還是真的很閒」 |
| Claude API 失敗 | 3 次重試 → 🔴 email + Status 留 inbox |
| 產出低於字數下限 | 再跑一次 + `temperature=0.8` 重寫 |
| Notion 寫入失敗 | 3 次重試 + 🔴 email + local markdown 備份 |
| 禁用字命中 | 🟡 email + 自動改寫一輪 |

## 測試

```bash
python scripts/draft.py --dry-run --category=daily
# 不寫 Notion 只 print markdown

python scripts/draft.py --source-id=<notion-page-id>
# 對單一 candidate 跑

python scripts/draft.py --voice-check
# 跑禁用字 / 字數 / 結構 lint
```

## 冪等性

同一個 candidate 已被寫過（Status = archived 且已有 draft 連結）→ skip。
可手動 `--force` override 重寫。

## 實作結構

```
skills/ai-column-draft/
  ├── SKILL.md
  ├── prompts/
  │   ├── voice.md         (手冊)
  │   ├── daily.md
  │   ├── news.md
  │   └── weekly.md
  ├── scripts/
  │   ├── draft.py         (主入口)
  │   ├── notion_reader.py
  │   ├── writer.py        (Claude call)
  │   ├── md_to_notion.py
  │   └── voice_lint.py
  └── tests/
      ├── test_voice_lint.py
      └── fixtures/
          └── sample_candidates.json
```

## 未來擴充（v2）

- [ ] 讓 Rick 在 Notion 建 `Tone Samples` database 存他喜歡的句子 / 不喜歡的句子 → few-shot 餵進 prompt
- [ ] A/B 兩版 draft 讓 Rick 選一個
- [ ] 用讀者點擊數據 feedback 回來調 prompt
