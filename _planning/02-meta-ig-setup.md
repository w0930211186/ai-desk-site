# Meta / IG Graph API 授權設定 — Rick 照這份一步步做

> 目標：拿到一個能讓我們自動 po 文 / 回私訊的「長期 access token」。這是 IG 自動化的入場券，沒這個什麼都動不了。流程有點繞 是 Meta 故意的 我陪你走一遍。

---

## 0. 事前準備 — 先確認以下四件事

1. **你有 Facebook 個人帳號**（任何舊的都可以）
2. **你的 IG 帳號是 Business 或 Creator**（不是 Private）
   - 打開 IG → 設定 → 帳號類型切換
3. **有一個 Facebook 粉絲專頁（Page）**
   - 還沒有就新建一個空的 叫「AI DESK」
4. **IG 帳號要「連結」到這個 Page**
   - Page 的設定 → Instagram → 連結 IG 帳號

如果這四件事還沒做完 IG Graph API 根本不讓你用。這是 Meta 的規矩不是我們的。

---

## 1. 建立 Meta Developer App

1. 到 https://developers.facebook.com
2. 右上角「我的應用程式 My Apps」→「建立應用程式 Create App」
3. 類型選 **Business**（不是 Consumer）
4. App 名字：`AI DESK Automation`（或任何你喜歡的）
5. Business Account：選你的 business portfolio（沒有就現場建一個免費的）
6. 建立完成 → 進入 App Dashboard

---

## 2. 加入兩個產品（Product）

在左邊 sidebar 找「Add Products」加下面兩個：

- **Instagram Graph API**（用來 po 文）
- **Facebook Login for Business**（拿 token 用）

加完後 sidebar 就會多兩個入口。

---

## 3. 設定 App 基本資訊

側邊 App Settings → Basic：
- App Domains：`ai-desk.netlify.app`（等網址確定再填）
- Privacy Policy URL：網站上線後一定要有 `/privacy.html`
- Category：`Business and Pages`
- 先存草稿 不用馬上送審

---

## 4. 拿「短期」access token（ 測試用 · 1 小時過期 ）

1. 到 https://developers.facebook.com/tools/explorer/
2. 右上角 App 選你剛建的 `AI DESK Automation`
3. User or Page 選 **Get User Access Token**
4. 加權限（Permissions），至少要這幾個：
   - `pages_show_list`
   - `pages_read_engagement`
   - `pages_manage_posts`
   - `instagram_basic`
   - `instagram_content_publish`
   - `instagram_manage_messages`（DM 漏斗要用）
   - `instagram_manage_comments`（監聽留言關鍵字要用）
   - `business_management`
5. 按「Generate Access Token」→ 授權 → 複製下來

這就是你的短期 token。**1 小時內會過期** 所以不能直接用在 skill 裡。

---

## 5. 用短期 token 換「長期」token（ 60 天 ）

把這個 URL 用 curl 或瀏覽器打開（替換三個值）：

```
https://graph.facebook.com/v19.0/oauth/access_token
  ?grant_type=fb_exchange_token
  &client_id=<你的 App ID>
  &client_secret=<你的 App Secret>
  &fb_exchange_token=<剛剛的短期 token>
```

回傳會看到 `access_token` 跟 `expires_in: 5183999`（≈ 60 天）。**這個就是長期 token** 存好。

---

## 6. 從長期 token 換「Page Token」（ 真正 po 文用的 token ）

打這個：

```
https://graph.facebook.com/v19.0/me/accounts?access_token=<長期 token>
```

回傳的 `data[]` 裡每一個 Page 都有自己的 `access_token`。挑你的「AI DESK」Page 那一個 `access_token` —— **這才是 IG po 文真正要用的 token**。

記下這兩個：
- `PAGE_ACCESS_TOKEN` — po 文 / 讀留言用
- `PAGE_ID` — 綁定的 Facebook Page 的 ID

---

## 7. 拿 IG Business Account ID

打這個：

```
https://graph.facebook.com/v19.0/<PAGE_ID>?fields=instagram_business_account&access_token=<PAGE_ACCESS_TOKEN>
```

回傳 `instagram_business_account.id` — 這就是 `IG_BUSINESS_ID`。

---

## 8. 測試 po 文（ container + publish 兩步 ）

**Step 1 · 建 container**（建立但先不發）
```
POST https://graph.facebook.com/v19.0/<IG_BUSINESS_ID>/media
  ?image_url=https://ai-desk.netlify.app/assets/og-cover.png
  &caption=測試 · AI DESK
  &access_token=<PAGE_ACCESS_TOKEN>
```
回傳一個 `id`（creation ID）。

**Step 2 · 正式 publish**
```
POST https://graph.facebook.com/v19.0/<IG_BUSINESS_ID>/media_publish
  ?creation_id=<上面的 id>
  &access_token=<PAGE_ACCESS_TOKEN>
```
回傳一個 media id = IG 上的貼文 ID。

Carousel 多張圖的話：每張圖先各建一個 container（`media_type=IMAGE, is_carousel_item=true`），再建一個 `media_type=CAROUSEL, children=<id1>,<id2>...` 的 container，最後再 publish。

---

## 9. App Review（送審 · 正式發布 前 要 做）

前面所有 token 都是「Development Mode」的 只能對你自己的 IG 用。要讓 skill 真的自動 po 到公開 IG 帳號 必須送審。

1. Dashboard → App Review → Permissions and Features
2. 對每一個 permission 申請（`instagram_content_publish` / `instagram_manage_messages` 等）
3. 每項要附：
   - 使用情境影片（你錄一段自己用 app 的 demo）
   - 資料處理說明（你怎麼處理用戶資料）
   - 測試帳號 / 測試步驟
4. Meta 審核 3-14 天

**重點**：送審門檻這幾年越來越高。有可能第一次被退。不要慌。

---

## 10. 維運 — 長期 Token 過期怎麼辦

長期 token ≈ 60 天。必須在過期前 refresh：

```
GET https://graph.facebook.com/v19.0/oauth/access_token
  ?grant_type=fb_exchange_token
  &client_id=<App ID>
  &client_secret=<App Secret>
  &fb_exchange_token=<現在還有效的長期 token>
```

建議 skill 架構：
- 每 50 天跑一次 refresh（scheduled-tasks）
- refresh 失敗 → Gmail draft 通知 Rick
- Rick 30 天內沒處理 → 所有 IG skill 停擺

---

## 11. 要存的環境變數（四組）

```
META_APP_ID            = <App ID>
META_APP_SECRET        = <App Secret>
META_PAGE_ID           = <Page ID>
IG_BUSINESS_ID         = <Instagram Business Account ID>
IG_LONG_LIVED_TOKEN    = <長期 Page Token · 每 50 天 refresh>
```

存在哪：
- 本機測試 → `.env` 檔案（加進 .gitignore）
- Netlify / 雲端 → Environment Variables
- Notion → 不要存 token 到 Notion（容易外洩）

---

## 常見故障排除

| 症狀 | 可能原因 |
|---|---|
| 401 Unauthorized | token 過期 / 權限不夠 → 重拿 token 或加 permission |
| 100 Invalid parameter | image_url 不能是 localhost 要公開可訪問的 URL |
| 190 Access token expired | 長期 token 超過 60 天 → refresh |
| (#100) Subfield 'image_url' | 圖片格式不對 / 檔案 > 8MB / URL 非 https |
| container status=ERROR | 圖片下載失敗 / caption 含特殊字 |
| "Application does not have capability" | permission 還沒過 App Review |

---

## Rick 要做的事（打勾）

- [ ] FB 個人帳號 OK
- [ ] IG 切 Business/Creator 模式
- [ ] 建立「AI DESK」粉絲專頁
- [ ] Page 與 IG 連結
- [ ] developers.facebook.com 建立 Business App
- [ ] 加入 Instagram Graph API + FB Login 兩個 product
- [ ] 填 App Basic Settings
- [ ] 拿短期 token 測試
- [ ] 換長期 token + Page Token
- [ ] 把五組環境變數給我
- [ ] （之後）送 App Review

這份做完 skill 那邊就能開工 IG 自動化這條。
