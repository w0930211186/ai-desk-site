# AI DESK 維運計畫 — 排程 / 錯誤通知 / 人工閥 / token refresh

> 「七點固定」不是一句話 是一整套後勤。下面是這套後勤的規格書。

---

## 一、每日時程表（固定班表）

| 時間 (CST) | 事件 | 觸發方式 | 失敗兜底 |
|---|---|---|---|
| 05:30 | `ai-column-scout` 跑 | scheduled-tasks cron | 3 次重試 → email draft |
| 05:45 | scout 完成 → 自動觸發 `ai-column-draft` | event chain | draft 失敗 → status 回 inbox |
| 06:00 | draft 完成 → email draft 通知 Rick「來看今天的稿」 | Gmail MCP | email 失敗 → log 留底 + SMS（v3 再做） |
| 06:00–06:55 | Rick 在 Notion 看 / 改 / 把 status 改 `ready` | 人工 | 如果 Rick 沒動 06:50 再發一封提醒 |
| 06:55 | `ai-column-ship` 三色燈檢查 | Notion webhook（status=ready） | 紅燈 → 卡住 + email / 綠燈 → 觸發 sync |
| 07:00 | `ai-journal-sync` 跑 → 官網上線 | 接 ship 綠燈 | git push 失敗 → email + 保留 local patch |
| 07:05 | `ai-ig-render` 產 carousel PNG | 接 sync 成功 | 圖產不出 → email 附 error trace |
| 07:05–12:00 | Rick DM 自己看 carousel → 回覆「OK」 | 人工 | Rick 沒動 → 當日 IG 跳過 |
| Rick 批准後 | `ai-ig-ship` 送 IG | 人工觸發 | API 失敗 → 3 次重試 → email |
| 即時 | `ai-dm-funnel` webhook | Meta → 我們的 endpoint | 一般 webhook 錯誤處理 |

---

## 二、週時程表（固定）

| 週幾 | 時間 | 事件 |
|---|---|---|
| 一、三、四、六 | 05:30 | Daily「AI 大事」流程 |
| 二、五 | 05:30 | Daily + News 深度（draft 會多一個 candidate） |
| 日 | 07:30 | Weekly「一週回顧」特別流程 — scout 改成掃過去 7 天 aggregate |
| 日 | 09:00 | 週回顧 sync + IG carousel（carousel 可以多到 10 張） |

---

## 三、Token / 憑證 refresh 排程

| 憑證 | 週期 | 怎麼處理 |
|---|---|---|
| IG Page Access Token | 60 天 | scheduled-task 每 50 天 refresh；還剩 7 天沒成功 → email 紅字警告 |
| Notion Integration Token | 永不過期 | 無 |
| Netlify 部署 hook | 永不過期 | 無 |
| GitHub PAT（push 用）| 根據你設的（建議 365 天）| 提前 14 天 email 提醒 |
| Meta App Secret | 永不過期 | 無 |

**Token 警告分級**
- 綠色：剩餘 > 15 天 → 靜默
- 黃色：剩餘 7-15 天 → 每日 email 一次
- 紅色：剩餘 < 7 天 → 每 6 小時 email 一次 + 首頁自動掛 banner「維運中」
- 黑色：已過期 → 所有依賴 skill 停擺 + email 每小時一次

---

## 四、錯誤通知格式（email draft 給 Rick）

所有失敗都寄到 **w0930211186@gmail.com**，subject 規範：

```
[AI DESK · 🔴 / 🟡 / 🟢] <skill name> · <事件摘要>
```

- 🔴 = blocker，整條管線卡住
- 🟡 = warning，部分失敗但繼續跑
- 🟢 = info，成功但需要你知道（例如 token 剩 10 天）

Email body 規範：
```
時間：YYYY-MM-DD HH:mm CST
Skill：<name>
狀態：🔴 / 🟡 / 🟢
事件：<一句話>

— 發生什麼 —
<error message>

— 我嘗試了什麼 —
1. ...
2. ...

— Rick 要做什麼 —
[ ] 具體動作 1
[ ] 具體動作 2

— 相關連結 —
Notion row: <url>
官網 URL: <url>
Log: <paste>
```

這個格式 skill 裡面寫成 template，failure 的時候 fill-in 直接 draft 進你 Gmail。

---

## 五、人工閥（兩道）

### 閥 #1 — draft → ready（每日 06:00-06:55）

Rick 在 Notion 看 draft：
- 可以直接改字 → 改完把 Status 切 `ready`
- 想重寫 → 點一下「重抽」按鈕（skill 再跑一次 draft）
- 不發 → Status 切 `skipped`（今日跳過不發）

過了 06:55 如果 Status 還在 `draft`：
- skill 自動卡住，不發布
- 寄一封 🟡 通知「今日跳過 / Rick 沒來得及看」
- 明天照常跑下一期

### 閥 #2 — IG carousel（每日 07:05 後）

render 完把圖片貼到 Notion 那條 row 的 `IG Preview` 欄位，Gmail draft 一封通知 Rick：
- 手機打開 Notion row
- 看 carousel OK → 在 Notion 把 `IG Approved` 欄位打勾
- 需要重產 → 改 `IG Caption` 欄位後點「重抽」
- 不發 IG → 什麼都不做（超時自動跳過）

---

## 六、Scheduled Tasks 清單（對應 mcp__scheduled-tasks）

```
task-01  每日 05:30 CST   ai-column-scout-daily
task-02  週日 04:30 CST   ai-column-scout-weekly  
task-03  每日 06:00 CST   email-notify-draft-ready
task-04  每日 06:50 CST   email-notify-draft-reminder
task-05  每 50 天         ig-token-refresh
task-06  每天 00:00 CST   healthcheck（全部 skill 上次成功時間）
task-07  每週日 23:00 CST weekly-analytics-digest
```

---

## 七、Healthcheck 規格（task-06）

每天 00:00 跑：
- 檢查 Notion API / GitHub API / Meta Graph API 三個都活著
- 檢查上次 scout / draft / sync 都在 24 小時內有成功
- 檢查 token 剩餘天數
- 任何異常 → 🔴 或 🟡 email

Rick 半夜不會看 email 所以只寄紅色 / 黑色等級，黃色等到早上第一輪再寄。

---

## 八、斷網 / API 中斷怎麼辦

**Notion 掛了**　scout 可以抓，draft 等 Notion 回來。超過 2 小時還沒回 → 🟡 email。

**GitHub 掛了**　sync 產好的 HTML 存 local，等 GitHub 回來批次 push。

**Netlify 掛了**　不用管，只是 build 慢一點。

**Meta API 掛了**　IG 當日跳過，照常發官網。

**Gmail MCP 掛了**　所有失敗通知改寫到本地 log 檔，每小時重試一次 email。

---

## 九、測試環境（下 skill 之前要有）

- 一個 Notion「AI DESK test」database（schema 跟正式一樣）
- 一個 test IG Business 帳號（Rick 用小號 / Dev Mode 下做）
- Netlify 另開一個 `ai-desk-staging.netlify.app` 連 `staging` branch
- GitHub repo 用 `main` = production / `staging` = test

所有新 skill 先在 staging 跑一週 no-bug 再切 production。

---

## 十、監控儀表（v3 再做 · 本階段跳過）

等整條管線跑順了 再做：
- 每日 scout 抓到幾條、draft 通過率、ship 通過率、IG 觸及、DM 觸發
- 放一個 /admin/ 隱藏頁（basic auth 擋）

現在階段 Rick 看 Gmail + Notion 就夠了 不用儀表。
