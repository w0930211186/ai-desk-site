---
name: ai-column-scout
description: AI DESK 每日情報雷達 — 掃 RSS / KOL / GitHub Trending / HN / arxiv 找當日 AI 大事。每天 05:30 CST 自動跑 也可當 Rick 說「掃一下今天 AI / 有什麼新 AI 消息 / scout / AI intel / 掃情報 / 看看今天 AI 圈」等類似指令時觸發。產出 3-5 條 candidate 寫進 Notion inbox 給下一個 skill 接手。
---

# ai-column-scout

獨立編輯台的情報抓取端。每日自動掃 + 排序 + 寫進 Notion inbox。

## 觸發詞

中文：掃情報、掃一下、今日 AI、看看 AI 圈、有什麼新 AI、什麼 AI 消息、scout、candidate 撈

English: scout, scan AI news, daily AI pulse, AI candidates, intel scan

## 依賴

**環境變數**
```
NOTION_TOKEN=secret_xxxx
NOTION_DATABASE_ID=xxxx
GITHUB_TOKEN=ghp_xxxx           # arxiv / github trending 要用
TWITTER_BEARER=AAAA...          # X/Twitter API v2 (optional, 有 free tier)
```

**資訊源清單**（`scripts/sources.yaml` 定義）
```yaml
rss:
  - name: "TechCrunch AI"
    url: "https://techcrunch.com/category/artificial-intelligence/feed/"
    weight: 1.0
  - name: "The Information AI"
    url: "..."
    weight: 1.2
  - name: "Stratechery"
    url: "https://stratechery.com/feed/"
    weight: 1.3
  - name: "Platformer"
    url: "https://www.platformer.news/feed"
    weight: 1.1
  - name: "Import AI (Jack Clark)"
    url: "https://jack-clark.net/feed/"
    weight: 1.4

twitter_users:
  - sama, elonmusk, sundarpichai, jack-clark, karpathy, gdb, jeffdean, drjimfan
  - weight_per_follower_rt: 0.8

github_trending:
  languages: [python, typescript]
  topics: [ai, llm, agent, langchain]
  window: 1d

hackernews:
  filter: "(AI|LLM|GPT|Claude|Anthropic|OpenAI)"
  min_score: 100
  min_comments: 20

arxiv:
  categories: [cs.AI, cs.CL, cs.LG]
  window_days: 1
```

## 執行流程

### 1. 並行抓取
各資訊源平行跑（asyncio / httpx），timeout 30s 每源。任何一源失敗 log 後跳過不崩整條。

### 2. 去重
按 URL 正規化（去 utm_* / 去 fragment）+ title fuzzy match（>85% similar 視為同一條）。

### 3. 評分（composite score 0-100）
```
score = w_source * source_weight
      + w_mentions * (被多源提到次數)
      + w_freshness * (越新分越高)
      + w_keyword_hit * (AI DESK 關注清單命中)
      + w_kol_signal * (重點 KOL 有轉發/引用)
```
關注清單（build-in）：
```
OpenAI, Anthropic, Google DeepMind, Meta AI, Mistral,
Nvidia, AMD, 新模型發布, benchmark, agentic, coding agent, 
多模態, voice model, tool use, RAG, 價格調整, API 變更,
EU AI Act, US AI order, safety, alignment
```

### 4. 挑 top 5
取分最高 5 條 寫進 Notion inbox：
```
Title: <原文 headline>
Status: inbox
Category: daily (週日特別跑改 weekly)
Sources: <URLs 多行>
Summary: 先自動產 50 字摘要 draft skill 會重寫
Tags: <自動從 source 推斷>
Notes: 
  - Source: <name>
  - Score: <value>
  - Signals: <哪些關鍵字命中>
```

### 5. 通知
把 5 條標題 list 出來 用 Gmail draft 發給 Rick：
```
Subject: [AI DESK · 🟢] scout · 今日 5 條 candidate

1. <title> · 87 分
2. <title> · 82 分
3. <title> · 76 分
...

全部進 Notion inbox:
https://notion.so/ai-desk/...

draft skill 會在 06:00 自動接力
```

## 週日特殊流程（Weekly）

Category 改 weekly；時間窗改 7 天；取當週分數最高的 10 條不只 5 條。

## 錯誤處理

| 情境 | 行為 |
|---|---|
| 全部資訊源都 fail | 🔴 email 紅色警告 + draft 跳過 |
| 單源 timeout | 🟡 每週彙整回報 |
| Notion 寫入失敗 | 3 次重試 + 🔴 email |
| 分數計算 NaN | 該條跳過 + log |

## 測試

```bash
python scripts/scout.py --dry-run
# 不寫 Notion 只 print 結果
python scripts/scout.py --source=hackernews
# 只跑一個源
```

## 實作結構

```
skills/ai-column-scout/
  ├── SKILL.md
  ├── scripts/
  │   ├── scout.py          (主入口)
  │   ├── sources.yaml      (資訊源設定)
  │   ├── fetchers/
  │   │   ├── rss.py
  │   │   ├── twitter.py
  │   │   ├── github.py
  │   │   ├── hn.py
  │   │   └── arxiv.py
  │   ├── scorer.py         (分數計算)
  │   └── notion_writer.py
  └── tests/
```
