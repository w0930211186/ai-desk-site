# AI DESK 開站資源取得清單 · 一小時走完

> Rick 選 IG/TG 帳號名 `ai_desk_tw`，選「全部一起做」。下面是 7 步手把手。每步我標了難度 + 時間 + 做完要給我什麼。任何一步卡住回來問。

---

## 進度勾選

- [ ] Step 1 · Notion integration + page
- [ ] Step 2 · GitHub repo
- [ ] Step 3 · Netlify 連 GitHub
- [ ] Step 4 · Telegram Bot
- [ ] Step 5 · Anthropic API key
- [ ] Step 6 · GitHub PAT
- [ ] Step 7 · Telegram 公開頻道

---

## Step 1 · Notion — ⭐ · 5 分鐘

### A. 建 page
1. 打開 https://notion.so → 進你的 workspace（個人版免費也 OK）
2. 左側 sidebar `+ New page`
3. 名稱打：`AI DESK 編輯台`
4. 頁面選「Blank」（空白頁）

### B. 建 Integration 拿 token
1. 新分頁開 https://www.notion.so/my-integrations
2. `New integration`
3. 填：
   - Name：`AI DESK Bot`
   - Associated workspace：選你上面建 page 的那個
   - Type：**Internal**（不要選 Public）
4. `Save`
5. 建好後會在頁面上看到 `Internal Integration Token` → 點 `Show` → 複製（長這樣 `ntn_xxxxxxxxxxxx`）

### C. 把 integration 邀進 page
1. 回到「AI DESK 編輯台」那個 page
2. 右上角 `···`（三個點）→ Connections → `+ Add connections`
3. 搜「AI DESK Bot」→ 點它 → 確認
4. 應該會出現 ✓ 綠勾

### D. 複製 page URL
瀏覽器網址列整串（長這樣 `https://www.notion.so/AI-DESK-編輯台-xxxxxxxxxxxxxxxxxxxxxxxxxx`）

### ✉️ 做完給我
```
1a. Notion token: ntn_xxxxx
1b. Notion page URL: https://notion.so/...
```

---

## Step 2 · GitHub repo — ⭐ · 3 分鐘

1. 打開 https://github.com（沒帳號 → 右上 Sign up 免費建）
2. 右上角 `+` → `New repository`
3. 填：
   - Repository name：`ai-desk-site`
   - Description：`獨立 AI 編輯台 · 每天 07:00 CST` （可選）
   - Visibility：**Public**
   - 三個勾：**全部不要勾**（不要 README / .gitignore / license）
4. `Create repository`

### ✉️ 做完給我
```
2. GitHub repo URL: https://github.com/你的username/ai-desk-site
```

---

## Step 3 · Netlify 連 GitHub — ⭐ · 3 分鐘

1. 打開 https://app.netlify.com
2. 沒帳號 → `Sign up with GitHub`（用 GitHub 帳號登入省事）
3. 登入後看到 dashboard → `Add new site` → `Import an existing project`
4. 點 `GitHub` → 授權 Netlify 存取你的 repos → 選 `ai-desk-site`
5. Build settings（全部空就對）：
   - Branch to deploy：`main`
   - Build command：**空著**
   - Publish directory：`.`（一個點）
6. `Deploy site` — 會失敗（因為 repo 還沒內容）沒關係
7. 進 Site 後：Site configuration → General → `Change site name` → 改 `ai-desk-tw`
8. 完成後 URL 變 `https://ai-desk-tw.netlify.app`

### ✉️ 做完給我
```
3. Netlify site: ai-desk-tw.netlify.app
```

---

## Step 4 · Telegram Bot — ⭐ · 3 分鐘

### A. 建 bot
1. 打開 Telegram → 搜尋 `@BotFather`（有藍色驗證打勾那個）
2. 點進去 → `/start`
3. 打 `/newbot`
4. BotFather 問名字：打 `AI DESK TW`
5. BotFather 問 username：打 `ai_desk_tw_bot`（必須 `_bot` 結尾）
6. BotFather 回一長串 token 長這樣：
   ```
   7123456789:AAHXXXXXXXXXXXXXXXXXXXXXXXXXXXX
   ```
   **複製起來貼到筆記本**（token 外洩 = bot 被盜）

### B. 拿你自己的 chat_id（給 bot 推通知要用）
1. 一樣在 Telegram 搜 `@userinfobot`
2. 點進去 → `/start`
3. 它會回你自己的 `Id: 123456789` — 那串數字就是 chat_id

### ✉️ 做完給我
```
4a. Telegram bot token: 7xxxxxxxxx:AAHxxx
4b. 你的 chat_id: 123456789
```

---

## Step 5 · Anthropic API key — ⭐ · 2 分鐘

1. 打開 https://console.anthropic.com
2. 用你現在登 Claude 的帳號登入
3. 左側 sidebar `API Keys` → `Create Key`
4. 名字打：`ai-desk`
5. `Create`
6. 出現 `sk-ant-xxxxx`（**只會看到一次** 關掉頁面就沒了）→ 貼筆記本

⚠️ API 是按量付費。daily skill 一天跑 1 次大約 $0.02-0.05 美元，一個月 < $2。月底看 usage 就知道。

### ✉️ 做完給我
```
5. Anthropic API key: sk-ant-xxxxx
```

---

## Step 6 · GitHub PAT — ⭐⭐ · 5 分鐘

1. 打開 https://github.com → 右上角頭像 → Settings
2. 左側最下面 Developer Settings
3. Personal access tokens → **Tokens (classic)**（不要選 Fine-grained）
4. `Generate new token` → `Generate new token (classic)`
5. 填：
   - Note：`ai-desk-bot`
   - Expiration：`365 days`
   - Scopes 勾：
     - ✓ **repo**（整個勾 含所有子項）
     - ✓ **workflow**
     - 其他不用勾
6. 最下面 `Generate token`
7. 出現 `ghp_xxxxxxxxxxxxxxxx`（**只會看到一次**）→ 貼筆記本

### ✉️ 做完給我
```
6. GitHub PAT: ghp_xxxxxxxxxxxx
```

---

## Step 7 · Telegram 公開頻道 — ⭐ · 5 分鐘

### A. 建頻道
1. Telegram 左上角 ✏️（寫訊息圖示）→ `New Channel`
2. 填：
   - 名字：`AI DESK · 每天 07:00 AI 大事`
   - 描述：`獨立 AI 編輯台。每天 07:00 一份。1 分鐘看完全球 AI 大事 · 每條附源。`
   - 照片：暫時可跳過 未來用 og-cover 的裁切圖
3. `Next` → 選 **Public Channel**
4. Username：`ai_desk_tw`（看有沒有被佔 被佔的話用 `aidesk_tw`）
5. `Create`

### B. 把 bot 加成 admin
1. 進頻道 → 右上頻道名 → Administrators → `Add Admin`
2. 搜 `ai_desk_tw_bot`（你第 4 步建的那個）
3. 權限：**Post Messages** 打勾就夠（其他不用）
4. 確認

### ✉️ 做完給我
```
7. Telegram 頻道: https://t.me/ai_desk_tw
   bot 已加 admin ✓
```

---

## 做完全部 7 步後 · 一次貼這段給我

複製下面模板填好再貼回聊天室：

```
1a. Notion token: 
1b. Notion page URL: 
2.  GitHub repo URL: 
3.  Netlify site: ai-desk-tw.netlify.app
4a. Telegram bot token: 
4b. Telegram chat_id: 
5.  Anthropic API key: 
6.  GitHub PAT: 
7.  Telegram 頻道: https://t.me/ai_desk_tw
```

貼回來後我會立刻：

1. 在 Notion 建 18 欄 database + 4 views（我自己來 你不用碰）
2. 把本地 `/outputs/ai-desk-site/` 推到你的 GitHub repo → Netlify 自動部署 → 1 分鐘後 `ai-desk-tw.netlify.app` 上線
3. 在 Telegram 用 bot 發一條測試訊息到你的 chat_id（確認通知通道 OK）
4. 建一條 Notion test row → 跑 ai-journal-sync → 看文章是不是真的出現在官網 + Telegram 頻道收到 push
5. 建 6 個 scheduled task（05:30 / 05:45 / 06:00 / 06:50 / 06:55 / 07:00）

整條管線今晚就能跑起來。IG 那邊先擺 因為它就是慢 不急。

---

## 資安提醒

上面有六個祕密 token（1a / 4a / 5 / 6 / 其餘不算）。給我的時候：
- 貼在這個聊天視窗 OK（Anthropic 後端不儲存 chat log 作訓練）
- **不要** 截圖公開發
- **不要** 存在 GitHub repo 裡（我會用 Netlify 環境變數 / Notion 欄位存，你不會看到明文）
- 任何一個外洩 → 回到對應平台重發一個就好（舊的廢掉）

---

## 卡住了怎麼辦

任何一步不確定 直接回來打「Step X 卡住 + 你看到的畫面描述」。我會對著你的描述帶你過。

Step 1 最容易卡 其他都很直白。Notion 我會教到你真的成功為止。
