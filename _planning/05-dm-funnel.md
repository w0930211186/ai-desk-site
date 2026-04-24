# DM 漏斗架構 — IG Messenger API 自建版本

> Rick 說工程量大沒關係 那就走自建。這份是最小可行架構（MVP）+ 未來擴充點。第一階段先做能 run 的最簡版 不打磨。

---

## 一、漏斗圖（讀者在 IG 上發生什麼）

```
[IG 貼文上線]
     │
     │ Rick 或系統在 caption / 留言 引導打關鍵字
     ▼
[讀者在貼文下留言「DESK」或 DM 打「DESK」]
     │
     ▼                                  (webhook 秒觸發)
[Meta 送 webhook 事件到我們 endpoint] ───────────────┐
     │                                                │
     ▼                                                │
[ai-dm-funnel skill 收到事件]                         │
     │                                                │
     ├─ 檢查是否在冷卻期（同一人 7 天內發過嗎）         │
     │    ├─ 是 → 靜默，不回                         │
     │    └─ 否 → 繼續                              │
     │                                                │
     ├─ 檢查是否已追蹤 AI DESK IG                     │
     │    ├─ 是 → 直接送 Notion 公開連結 DM            │
     │    └─ 否 → 送「請先追蹤再 DM 回覆 READY」      │
     │                                                │
     ▼                                                │
[等讀者回覆 READY]                                    │
     │                                                │
     ▼                                                │
[再次檢查追蹤 → 是 → 送 Notion 連結]  ────────────────┘
     │
     ▼
[寫 log 到 Notion「DM 漏斗記錄」database]
     │
     ▼
[Rick 週末看一次 DM 漏斗報告]
```

---

## 二、需要建的東西

### 1. webhook 接收端（最頭痛的一步）

Meta 會把事件 POST 到一個你指定的 URL。這個 URL 必須：
- 公開可訪問（HTTPS）
- 能 5 秒內回 200
- 能驗證 X-Hub-Signature-256 header

**部署方案三選一**：

| 方案 | 成本 | 優點 | 缺點 |
|---|---|---|---|
| **Netlify Functions** | 免費（每月 125k 次） | 跟官網同 repo | 冷啟動慢 |
| **Cloudflare Workers** | 免費（每日 100k 次） | 反應快 全球 edge | 要另設 domain |
| **Vercel Functions** | 免費（每月 100GB） | Node.js 生態全 | 監控較弱 |

**推薦 Netlify Functions** — 因為官網已經在 Netlify。一個 repo 一個 deploy 省事。

`netlify/functions/ig-webhook.js`：
```javascript
exports.handler = async (event) => {
  // GET = Meta verify challenge
  if (event.httpMethod === 'GET') {
    const mode = event.queryStringParameters['hub.mode'];
    const token = event.queryStringParameters['hub.verify_token'];
    const challenge = event.queryStringParameters['hub.challenge'];
    if (mode === 'subscribe' && token === process.env.META_VERIFY_TOKEN) {
      return { statusCode: 200, body: challenge };
    }
    return { statusCode: 403, body: 'forbidden' };
  }
  // POST = 事件進來
  if (event.httpMethod === 'POST') {
    // 驗證 signature
    // 解析 entry → messaging/comments 事件
    // 丟到 queue / Notion / 直接處理
    return { statusCode: 200, body: 'ok' };
  }
};
```

### 2. Meta 端設定

1. 回到 Meta Developer App
2. sidebar → Webhooks
3. Object: `instagram`
4. Callback URL: `https://ai-desk.netlify.app/.netlify/functions/ig-webhook`
5. Verify Token: 自己定一個 random string 存到 Netlify env var
6. Subscribe fields: `messages` + `message_reactions` + `comments` + `live_comments`

### 3. 追蹤狀態檢查（最難的一步）

**壞消息**：IG API 不直接給你 followers list。
**好消息**：但可以用 workaround —

當讀者跟你 DM 互動時 payload 裡有 `sender.id`（IG Scoped ID）。呼叫：
```
GET https://graph.instagram.com/v19.0/<USER_ID>?fields=is_follower&access_token=<TOKEN>
```

但 — `is_follower` 這個 field 只有 Business Account 的某些情境下可得。

**實際做法（第一階段）**：
- 不做真的 follow check
- DM 第一輪回覆：「先追蹤 AI DESK → 回覆 READY → 我 DM 送你今日連結」
- 信任系統，讀者 100% 追蹤才會 follow-reply
- 第二階段再接 webhook 的 `follows` 事件記帳

### 4. Notion「DM 漏斗記錄」database（另建一個）

欄位：

| 欄位 | 類型 | 說明 |
|---|---|---|
| IG User ID | Title | sender id |
| IG Username | Rich text | 顯示名 |
| 關鍵字 | Rich text | 觸發的 keyword |
| 首次觸發時間 | Date | |
| 狀態 | Select | `hello-sent` / `ready-received` / `link-sent` / `cooled` |
| 送出的文章 | Relation | 指向主 database |
| 本週 DM 次數 | Number | 冷卻判定用 |
| 備註 | Rich text | |

---

## 三、關鍵字設計（第一版 · 簡單）

放在 IG caption 底下固定一段：

```
想看完整版？留言「DESK」或 DM「DESK」
我會把今天的 Notion 公開連結傳給你 ✉️
```

觸發關鍵字（大小寫不敏感）：
- `DESK`
- `desk`
- `AI DESK`
- `aidesk`
- `READ` / `讀`

其他都不處理。

---

## 四、DM 話術（三段）

### Step 1 · 讀者第一次觸發「DESK」

```
Hi 👋 AI DESK 編輯台

謝謝你想看完整版！
我的規矩很簡單 ——

👉 先追蹤一下 @ai_desk_official
👉 追完回覆「READY」給我
👉 我立刻把今日 Notion 完整連結 DM 給你

這是獨立編輯台唯一的交易 — 不賣廣告
只要你追蹤就送閱讀權限 合理吧？
```

### Step 2 · 讀者回「READY」

```
收到 ✉️

今日 AI 大事完整版：
https://notion.so/ai-desk/YYYY-MM-DD-xxxxx

📍 1 分鐘看完 · 每條附源
📍 明天 07:00 一樣的時間見

想訂閱每日推播？
官網 → ai-desk.netlify.app 右下角 email 欄
```

### Step 3 · 同一人 7 天內再觸發

```
你這週已經拿過連結了 🌚
明天 07:00 上線的那期 再來找我
```

（冷卻機制 避免被當 spam）

---

## 五、Attribution 追蹤（讀者從哪來）

每次送 Notion 連結時 URL 帶 UTM：

```
https://notion.so/ai-desk/2026-04-24-ai-daily?utm_source=ig&utm_medium=dm&utm_campaign=daily_funnel&ref=<IG_user_scoped_id>
```

Notion public page 的分析整合 Google Analytics 4（或 Plausible）:
- 看 IG DM 來的流量
- 看哪一期文章觸發最多 DM
- 看 follow-first 到 ready 轉換率

---

## 六、對 Meta 政策的遵守（不能忽略）

Meta 對 auto-DM 有規範：

- **24 小時規則**：你只能在讀者最後一次互動的 24 小時內 DM
- **「人類介入」label**：超過 24 小時要加 `HUMAN_AGENT` tag（而且必須真的有人類介入）
- **不能群發**：只能 1-to-1 對話
- **不能假冒**：不能用別人名字 / logo

我們的漏斗設計是 ✅ 符合的（只在讀者主動觸發後 24 小時內回）

---

## 七、三階段實作進度

### 階段 1（MVP · 本季做）
- webhook endpoint 建好（Netlify Function）
- Meta 端 subscribe instagram webhook
- 關鍵字觸發 → Step 1 / 2 兩段話術
- Notion 記錄 database
- 無 follow check，信任系統
- 冷卻 7 天

### 階段 2（下季）
- follow check via webhook `follows` 事件
- Daily 特別連結 vs News 深度特別連結（分流）
- 整合 Plausible / GA4 追蹤轉換

### 階段 3（明年）
- ManyChat-like 多段對話樹
- 訂閱機制（讀者可選每天 / 每週被動推送）
- A/B 測試不同話術

---

## 八、Rick 要做的事

- [ ] 決定 IG 帳號名字（建議 `ai_desk_official` / `aidesk.press` / `ai_desk_tw`）
- [ ] 確認走 Netlify Functions
- [ ] Meta IG 授權（前一份文件）
- [ ] 確認話術（上面三段要不要改語氣）
- [ ] 建 Notion「DM 漏斗記錄」database 並授權 integration

做完 skill 我就能實作。
