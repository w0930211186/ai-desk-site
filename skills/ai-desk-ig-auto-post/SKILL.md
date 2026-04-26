---
name: ai-desk-ig-auto-post
description: AI DESK daily 文章發布完之後，自動把 story.png 透過 Meta Business Suite Web 介面（不走 Graph API、不需 App Review）發到 IG @ai_desk_0424 跟 FB AI DESK Page 限動。整個流程 0 觸碰：產圖 → 開 Business Suite → JS 注入圖片 → drop → 點分享 → Telegram 通知用戶完成。當 ai-desk-publish 完成後自動觸發，或當使用者說「自動發 IG / auto post IG / 全自動 IG / 推 IG / IG 自動發布 / 跑 IG / IG 上架」等類似指令時觸發。需要使用者 Mac Chrome 開著且 FB 已登入。
---

# ai-desk-ig-auto-post

每日 daily 文章自動發 IG + FB 限時動態。**繞 Meta Graph API**，直接走 Business Suite Web 介面 + Chrome MCP 自動化。

## 為什麼不走 Graph API

`instagram_content_publish` 權限被 Meta 鎖在 App Review 後（5-10 天等審核 + 可能被打槍）。Business Suite Web 介面**已經內建可發 IG/FB 限動**，且不需要任何 API 權限申請。我們用 Chrome MCP 模擬使用者操作即可。

## 觸發詞

中文：自動發 IG / 全自動 IG / 推 IG / IG 自動發布 / 跑 IG / IG 上架 / 上限動 / 自動限動

English: auto post IG / publish IG story / push to IG / auto IG / IG auto

## 前置條件（一次性，不用每天做）

| 項目 | 狀態 | 備註 |
|---|---|---|
| FB Page `AI DESK` | ✅ 已建 | Page ID `61562839956251` |
| IG @ai_desk_0424 連到 Page | ✅ 已連 | Asset Portfolio `1141294485727223` |
| Mac Chrome 開著 | ⚠️ 每天 | 必須開機 + Chrome 開 |
| FB 帳號登入狀態 | ⚠️ 每月一次 | cookies 過期要重 login |
| Claude in Chrome extension | ✅ 已裝 | + Act without asking ON |
| ai-desk-ig-story skill | ✅ 已裝 | 產 story.png |

### Chrome 擴充功能權限（一次設好，0 觸碰前提）

在 Chrome 右上角 Claude 擴充功能 icon 點開 → **business.facebook.com** 站點設定：

- ✅ **On all sites** 或 **business.facebook.com** 設成 Always allow
- ✅ **Act without asking** ON
- ✅ **Allow clicking submit-style buttons**（一定要勾，不然「分享」按鈕點擊會被擋）
- ✅ **Allow JavaScript injection**（drop event 需要）
- ✅ **Allow file uploads**（file_upload tool 需要）

⚠️ **沒勾「Allow clicking submit-style buttons」會怎樣**：
圖會自動上傳 + 預覽出來，但最後一步「分享」按鈕被擋 → Telegram 收到「⚠️ 分享按鈕被擋，請手動點」 → 你還是要碰。設好之後才是真 0 觸碰。

## Cowork 排程設定

接在 ai-desk-publish 後面：

```yaml
name: ai-desk-ig-auto-post
schedule: daily 07:15 CST
chain_after: ai-desk-publish
trigger_on_demand: true
```

## 執行流程

### Step 1 · 產 story 素材
呼叫 `ai-desk-ig-story` skill：
- 讀今日最新 daily HTML（從 GitHub raw 或本地 repo）
- Pillow 產 1080×1920 PNG
- 寫到本地 `~/Downloads/ai-desk-ig-stories/<YYYY-MM-DD>/story.png` + `caption.txt`

### Step 2 · 透過 Chrome MCP 開 Business Suite

用 Claude in Chrome 的 `navigate` 工具：

```
https://business.facebook.com/latest/story_composer/?asset_id=1141294485727223&business_id=1274367634384629
```

等 page load（~3 秒）。

### Step 3 · 把 story.png 注入瀏覽器並 drop 到上傳區

#### 3a. 讀本地 PNG → base64 切 18KB chunks

```python
from pathlib import Path
import base64

png = Path.home() / 'Downloads' / 'ai-desk-ig-stories' / DATE / 'story.png'
b64 = base64.b64encode(png.read_bytes()).decode()
chunks = [b64[i:i+18000] for i in range(0, len(b64), 18000)]
# 通常 12-17 個 chunks（PNG ~150-220 KB）
```

#### 3b. 多次 `javascript_exec` 把 chunks 設到 window vars

對每個 chunk：
```js
window.b64_<i> = "<chunk content>";
```

#### 3c. 最後一次 JS 組合 + 建 File + dispatch drop event

```js
((async () => {
  const chunks = [];
  for (let i = 0; window['b64_' + i]; i++) chunks.push(window['b64_' + i]);
  const b64 = chunks.join('');

  const bytes = Uint8Array.from(atob(b64), c => c.charCodeAt(0));
  const file = new File([bytes], 'story.png', {type: 'image/png', lastModified: Date.now()});

  const zone = Array.from(document.querySelectorAll('div')).find(d =>
    /將相片或影片拖放到這裡/.test(d.textContent) && d.textContent.length < 200 && d.offsetParent
  );

  const dt = new DataTransfer();
  dt.items.add(file);

  for (const e of ['dragenter', 'dragover', 'drop']) {
    zone.dispatchEvent(new DragEvent(e, {bubbles: true, cancelable: true, dataTransfer: dt}));
  }

  // clean up
  for (let i = 0; window['b64_' + i]; i++) delete window['b64_' + i];

  return { ok: true, fileSize: file.size };
})())
```

### Step 4 · 等 Meta 處理上傳（5-8 秒）

等 preview 出來。可以 poll 看畫面文字變化（從「將相片或影片拖放到這裡」變成預覽）。

### Step 5 · 確認 IG + FB 都打勾

預設 Business Suite 兩個都會勾，但保險起見 JS 確認：

```js
// 找「分享到」combobox 確認文字含 ai_desk_0424 + AI DESK
const shareTo = document.body.innerText.match(/分享到[\s\S]{0,50}/);
```

### Step 6 · 點「分享」按鈕

```js
const shareBtn = Array.from(document.querySelectorAll('div[role="button"], button'))
  .find(b => b.textContent.trim() === '分享' && b.offsetParent);
shareBtn.click();
```

### Step 7 · 等 5 秒看成功訊息

```js
const success = document.body.innerText.includes('你的限時動態已發佈');
```

### Step 8 · Telegram 通知用戶

呼叫 `send_telegram.py` 發訊息：

```
✅ AI DESK · IG 限動自動發布完成

N°XX · MM/DD daily
✓ FB AI DESK Page
✓ IG @ai_desk_0424

🌐 全文：https://ai-desk-tw.netlify.app/posts/<slug>.html
🔗 IG：instagram.com/ai_desk_0424
```

## 失敗 fallback

如果任一步失敗：
1. 截圖目前 Chrome 畫面
2. 推 Telegram 警示用戶 + 附截圖
3. 用戶手機收到 → 手動發（30 秒）
4. ai-desk-ig-story 既有的 Telegram 推送照常跑，用戶有素材

常見失敗：
- **Chrome 沒開** → Telegram 警示「Mac Chrome 沒開機，今日 IG 跳過」
- **FB session 過期** → 警示「請手動 login Facebook」
- **drop zone 找不到** → Meta UI 改了，需更新 selector
- **分享按鈕灰** → 可能 IG/FB 沒同時勾，重試

## 測試步驟

```bash
# 在 Cowork 開新對話打：
> 跑 ai-desk-ig-auto-post

# 應該看到：
# 1. 產 PNG 完成
# 2. Chrome 開 Business Suite
# 3. 圖片注入 + drop 完成
# 4. 點分享
# 5. 收到 Telegram「✅ 已自動發布」
# 6. IG @ai_desk_0424 多 1 則限動
```

## 後續優化路徑

短期（這週）：
- 加重試邏輯（drop 失敗自動 retry 3 次）
- 加截圖記錄（每天存一張上傳完成的截圖到 ~/Downloads/）
- 加 link sticker（IG Story 可在圖片上加文章連結貼紙）

中期（這月）：
- 走 Meta App Review 拿 `instagram_content_publish` 權限
- 通過後切換到 Graph API（不需 Chrome 開機）

長期：
- 加 IG Reels 自動發布（從 daily 文章產短影音）
- 加 Threads 自動發布
- 加 LinkedIn 自動發布
- 多平台 hub-and-spoke 全部由 publish 觸發

## 安全提醒

- Business Suite session 屬於用戶個人 FB 帳號，自動化操作有「被 Meta 風控誤判」風險（雖然每天一次低頻不太會）
- 萬一 Meta 警告，立即停掉自動化，改回 Telegram 半自動 + 加 App Review

---

— END
