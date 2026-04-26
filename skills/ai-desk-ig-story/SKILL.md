---
name: ai-desk-ig-story
description: 把當天 AI DESK 發的 daily 文章自動產一張 1080×1920 mono brutalist 風 IG Story PNG 加 caption 跟 hashtag 草稿，丟到 ~/Downloads/ai-desk-ig-stories/<date>/。當使用者說「產 IG story、IG 素材、發限動、ig-story、daily ig、出 story、做今天的 IG」等類似指令時觸發。也適合接在 ai-desk-publish 排程任務後面自動跑。任務完成後從 Discord/Notion 通知使用者「素材好了」，使用者再手動上傳 IG（30 秒）。半自動 editorial 控制權留給使用者。
---

# ai-desk-ig-story

AI DESK 每日 IG Story 半自動素材產生器。從一篇 publish 完的 daily HTML 抽資料，生 mono brutalist 風 1080×1920 PNG + 中英雙語 caption + hashtag。

## 為什麼半自動

完整 IG Graph API 自動發 story 需要 Meta App Review (5-10 工作天) + 60 天 token refresh + business account verification。**這個 skill 跳過所有這些**，直接生素材。使用者保留 editorial 控制（要不要發、改 caption、選時機）。

→ 全自動版本之後再做（task: ai-desk-ig-graph-publish）。

## 觸發詞

中文：產 IG story、做 IG 素材、發限動素材、生今天的 IG、IG story、ig-story、daily ig、ig 素材

English: generate ig story, ig story draft, daily ig, ig content, story material

## 依賴

**檔案**
- `posts/<latest-daily>.html` — 當天 daily 文章 (ai-desk-publish 產出)
- `skills/ai-desk-ig-story/fonts/InterTight-VF.ttf` — Latin 字型
- `skills/ai-desk-ig-story/fonts/NotoSansCJKtc-Black.otf` — 中文標題
- `skills/ai-desk-ig-story/fonts/NotoSansCJKtc-Regular.otf` — 中文正文

**Python 套件**
- Pillow (`pip install Pillow`)

## 執行流程

### 1. 找最新 daily
從 `posts/` 資料夾找今日 daily：
```bash
TODAY=$(date +%Y-%m-%d)
LATEST=$(ls posts/${TODAY}*-ai-daily.html 2>/dev/null | tail -1)
```

如果今天沒 daily（例如週日只發 weekly），改找最近一篇：
```bash
LATEST=$(ls posts/*-ai-daily.html | sort | tail -1)
```

### 2. 跑 generator

```bash
python3 skills/ai-desk-ig-story/scripts/generate.py "$LATEST"
```

預設輸出到 `~/Downloads/ai-desk-ig-stories/<YYYY-MM-DD>/`。

### 3. 通知使用者

排程任務完成後發 Discord 通知（透過 ai-desk 既有的 `discord-journal-notify-daily` 或新增一個 hook）：

```
📸 [AI DESK] IG story 素材已備好

N°02 · 04/24 daily
✓ ~/Downloads/ai-desk-ig-stories/2026-04-24/story.png (1080×1920)
✓ caption.txt（中英雙語 + 17 hashtag）

打開 IG App → 加限動 → 選那張 PNG → 貼 caption → 發。
30 秒搞定。
```

或同時推到 Notion 「IG 素材待發」資料庫，產 row 含縮圖。

### 4. 使用者手動發 IG（30 秒）

1. 開手機 IG App → ai_desk_0424 帳號
2. 加限動（左上 ＋ 圖示 → 限時動態）
3. 從相簿選 `story.png`
4. 點下方文字工具或標籤 → 貼 caption.txt 內容（IG 限動 caption 區其實只能放短文字，建議只貼 hashtag 或關鍵字到貼紙）
5. 發布

**註**：IG Story 跟 IG Feed 不同 — story 沒有大塊 caption 區，hashtag 用「文字貼紙」加。但這個 caption.txt 同時當「分享連結 + comment 草稿」用，你可以：
- 截圖 story
- 同一張圖也發成 feed post（feed 才有大 caption 區）
- 或只發 story 但 caption.txt 留作 newsletter 摘要

## 輸出格式

**story.png** (1080×1920, mono brutalist)
```
┌─────────────────────────────┐
│ ■ AI DESK            N°02   │  ← 頭部 lockup + edition
│ 2026·04·24·FRI    DAILY·AI 大事│  ← 日期 + 分類
│ ─────────────────────       │
│                             │
│ 2026/04/24 · AI 大事         │
│ · GPT-5.5、Claude            │  ← 標題（Noto Black 78pt）
│ Code postmortem、            │
│ AI code 裂開源               │
│                             │
│ — KEY SIGNALS               │  ← 小標
│                             │
│ ◆ 模型迭代節奏被對手逼到...  │  ← 3 個 keypoints
│   GPT-5.5 只隔 GPT-5...      │
│                             │
│ ◆ AI 透明度標範...           │
│ ...                         │
│                             │
│ ─────────────────────       │
│ READ FULL · 全文＋源     →   │  ← CTA
│ ai-desk-tw.netlify.app      │
│                @ai_desk_0424│
│   © AI DESK · Independent   │
└─────────────────────────────┘
```

**caption.txt**
```
<title>

— N°<edition> · <date> —

<summary>

◆ <keypoint 1>
◆ <keypoint 2>
◆ <keypoint 3>

····

全文 · 附源 · 附判斷
ai-desk-tw.netlify.app

#AIDESK #AI大事 #AINews #獨立編輯台 #AIDailyBrief #AI #editorial
#monobrutalist <文章專屬 hashtags>
```

## Cowork pipeline 接入

排在 `ai-desk-publish` 任務後面：

```yaml
# Cowork scheduled task
name: ai-desk-publish
schedule: daily 07:00 CST
chain:
  - ai-desk-ig-story  # ← 加這個
  - discord-journal-notify-daily
```

或單獨：
```yaml
name: ai-desk-ig-story
schedule: daily 07:15 CST  # publish 完 15 分鐘後跑
trigger_on_demand: true
```

## 樣板調整

如果之後要改視覺：
- **顏色**：純黑底 + 純白字 + #8A8A8A mute 灰 + #5A5A5A copyright 灰。要改 brand 主色直接編輯 `generate.py` 內 `(0, 0, 0)` / `(255, 255, 255)` 等
- **字體**：替換 `fonts/` 目錄內檔案。注意 Pillow 需要 .ttf 或 .otf
- **版型**：edit `render_story()` 內的 y 座標 + sizes
- **caption 風格**：edit `generate_caption()` 函式
- **hashtag 策略**：edit `base_tags` 跟 `content_tags` 對照表

## 已知限制

1. **caption.txt 適合 IG Feed Post，不適合直接貼到 Story**
   IG Story 沒大 caption 區，只能用「貼紙」加文字。建議用法：story.png 配合 hashtag 貼紙；同一張圖也當 feed post 發，feed 用 caption.txt 全內容。

2. **手機自動上傳暫不支援**
   需要 Meta Graph API + App Review。看 task `ai-desk-ig-graph-publish` 之後做。

3. **字體 OFL 授權**
   Inter Tight 跟 Noto Sans CJK 都是 OFL，可商業使用。`fonts/` 內檔案直接 bundle 在 repo 即可，不需要 runtime 下載。

## 測試步驟

```bash
# 1. 先確認字體在
ls skills/ai-desk-ig-story/fonts/

# 2. 跑 generator
python3 skills/ai-desk-ig-story/scripts/generate.py \
  posts/2026-04-24-ai-daily.html \
  /tmp/test-output

# 3. 開來看
open /tmp/test-output/story.png
cat /tmp/test-output/caption.txt
```

預期產出：
- `story.png` (1080×1920, ~150 KB)
- `caption.txt` (~700 chars 含 hashtag)
