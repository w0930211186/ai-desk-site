#!/usr/bin/env python3
import json, sys

PULSE_PATH = "/home/user/ai-desk-site/data/pulse.json"

new_items = [
    {
        "id": "pulse-2026-05-23-08-japan-megabanks-anthropic-mythos",
        "ts": "2026-05-23T08:10:00+08:00",
        "title": "日本三大銀行本月底接入 Anthropic Mythos · 美日財政部協調確認亞洲金融體系首批存取授權",
        "source": "Nikkei Asia",
        "url": "https://asia.nikkei.com/business/finance/japan-megabanks-to-gain-access-to-anthropic-s-powerful-ai-model-mythos",
        "blurb": "MUFG、SMBC、Mizuho 將於五月底首度取得 Claude Mythos 的受限存取授權，成為 Glasswing 計畫首批亞洲機構；此舉由美日財政部長本週東京峰會協調達成，日本同步組建 36 機構公私工作組追蹤 Mythos 級別金融網路安全風險。",
        "editorial": "<p><strong>第一</strong>　日經亞洲（Nikkei Asia）5 月 22 日報導，三菱 UFJ 金融集團（MUFG）、三井住友金融集團（SMBC）及瑞穗金融集團（Mizuho）預計於五月底以 Glasswing 合作夥伴條款取得 Anthropic Claude Mythos 的受限存取授權，成為 Mythos 預覽計畫的首批非西方機構。消息源自美國財政部長 Scott Bessent 本週赴東京與三大行及日本財務大臣的系列會面。日本財務大臣同步宣布，以三大銀行、日本銀行、Anthropic 及 OpenAI 日本法人為核心，組成 36 機構的公私聯合工作組，任務是在六個月內完成 Mythos 級別 AI 網路攻擊能力的系統性風險評估框架。Mythos 在 Glasswing 框架下交付時設有嚴格限制：合作方可掃描自身系統漏洞並獲取修補建議，不得對外披露漏洞利用程式碼。</p><p><strong>第二</strong>　此舉是 AI 攻擊性安全能力首度被納入美日同盟數位合作框架的制度性信號。Glasswing 計畫此前的合作夥伴以美國科技巨頭（AWS、Apple、Cisco、Google、Microsoft）和少數歐洲機構為主，日本三大行的接入由政府協調而非純商業談判驅動，標誌著美國政府已將 Mythos 的存取授權視為同盟數位安全外交的一部分，可預期南韓、澳洲等同盟夥伴機構的接入談判在此後加速。對全球金融監管機構而言，Mythos 已由 CISA 及五眼聯盟指引確認為系統性網路風險來源，日本成立 36 機構工作組是亞洲在 AI 安全監管框架上的快速補位，亦是全球主要金融市場在 AI 攻擊性能力的監管協調機制快速並聯的可見前緣。</p><p><strong>第三</strong>　對 BEXS 黃金交易學員而言，日本三大銀行是全球外匯與固定收益市場的核心流動性提供方，此次 Mythos 存取若在六個月工作組評估後觸發日本金融廳（FSA）的 AI 工具使用新規，相關合規成本的影響可能在 FY2027 對三大行的運營成本基準產生初步可量化影響，是追蹤亞洲金融機構 AI 轉型合規成本的早期觀察節點。對企業 CIO 而言，以 AI 輔助漏洞掃描為核心的主動安全防禦正在成為頂尖金融機構的標準流程，建議在 Q3 前評估企業當前滲透測試框架是否需要引入 AI 輔助掃描環節，Glasswing 夥伴陸續公開的工具和程式碼是選型的低成本起點。</p>"
    },
    {
        "id": "pulse-2026-05-23-08-pope-leo-magnifica-humanitas-ai-encyclical",
        "ts": "2026-05-23T08:10:00+08:00",
        "title": "教宗良十四世 AI 通諭《Magnifica Humanitas》後天發布 · Anthropic 共同創辦人同台、道德主體正式切入 frontier 治理討論",
        "source": "Vatican News / Fortune",
        "url": "https://www.vaticannews.va/en/pope/news/2026-05/pope-leo-xiv-first-encyclical-magnifica-humanitas.html",
        "blurb": "教宗良十四世 5 月 15 日親署首份 AI 主題通諭，定於 25 日在梵蒂岡發布，主題聚焦「人工智能時代的人格保護」；Anthropic 共同創辦人、可解釋 AI 研究負責人 Christopher Olah 受邀同台，良十四世親自出席屬創教宗先例，同步設立梵蒂岡 AI 委員會。",
        "editorial": "<p><strong>第一</strong>　梵蒂岡新聞社 5 月 18 日確認，教宗良十四世（Pope Leo XIV）將於 5 月 25 日上午 11 時 30 分在梵蒂岡宗教廳（Synod Hall）發布首份通諭《Magnifica Humanitas》（人的偉大尊嚴），核心主題是「人工智能時代的人格保護」。良十四世於 5 月 15 日親署本文件，與 135 年前良十三世簽署《勞工問題》（Rerum Novarum）同日；教宗親自出席自身通諭發布儀式屬創教宗先例。演講嘉賓包含 Anthropic 共同創辦人兼可解釋 AI 研究負責人 Christopher Olah。梵蒂岡同步於 5 月 18 日宣告設立常設 AI 委員會，以通諭框架為基礎持續追蹤政策演進。全球天主教信眾約 13 億，梵蒂岡在道德外交層面的認可效力覆蓋 UN 成員國中多數具影響力的政府與非政府組織框架。</p><p><strong>第二</strong>　良十四世選擇 Anthropic 代表而非 OpenAI 或 Google 同台，是可讀的機構信任訊號：Anthropic 的憲法式 AI（Constitutional AI）框架與對可解釋性研究的公開投入，符合梵蒂岡「AI 系統可理解、可問責」的道德要求。良十四世以《勞工問題》週年日簽署本文件，建立了明確的道德傳承定位：《勞工問題》在 1891 年工業革命期間奠定了全球勞工保護原則的宗教-政策框架，《Magnifica Humanitas》的相似定位意味著梵蒂岡正在建構一個可在 AI 監管討論中供各國政府援引的道德錨點。這是 Anthropic 繼比爾蓋茲基金會之後，在 AI 安全形象建設上的第二個頂級非商業機構背書，且背書維度從全球公衛延伸至宗教道德主體，覆蓋的受眾地理範疇超越前者。</p><p><strong>第三</strong>　對 BEXS 學員而言，Anthropic 在 8 個月內連續獲得比爾蓋茲基金會和梵蒂岡兩個頂級非商業機構背書，是 Anthropic IPO 路演中 ESG 章節可直接援引的具體背書記錄，對主權財富基金及退休基金等 ESG 敏感型機構投資人的吸引力高於純商業指標，是下一輪融資及 IPO 定價敘事的正向材料。對一般 AI 從業者而言，Olah 在梵蒂岡的演講是「可解釋 AI 技術定義如何在全球治理語境中取得非技術共識」的早期觀察節點，通諭對 AI 透明度的措辭在未來三至五年可能成為歐盟 AI Act 後續修訂及南美監管框架的參照文本，值得在發布後追蹤通諭措辭的具體政策回響。</p>"
    },
    {
        "id": "pulse-2026-05-23-08-sap-prior-labs-1b-tabular-ai-europe",
        "ts": "2026-05-23T08:10:00+08:00",
        "title": "SAP 逾 10 億歐元收購德國 Prior Labs · 結構化資料基礎模型進入 Frontier 量級、歐洲企業 AI 實驗室首現旗艦競爭者",
        "source": "TechCrunch / SAP News",
        "url": "https://techcrunch.com/2026/05/05/sap-bets-1-16b-on-18-month-old-german-ai-lab-and-says-yes-to-nemoclaw/",
        "blurb": "SAP 5 月 4 日宣布收購德國弗萊堡 Prior Labs，承諾四年逾 10 億歐元打造歐洲 Frontier AI 研究機構；Prior Labs 的 TabPFN 模型以單次前向傳遞取代梯度提升訓練、於 Nature 發表、逾 300 萬次下載，SAP 下注的是 LLM 以外最具企業資料密度的結構化 AI 範式。",
        "editorial": "<p><strong>第一</strong>　2026 年 5 月 4 日，SAP SE 宣布收購德國 AI 研究新創 Prior Labs，SAP 承諾四年投入逾 10 億歐元，以 Prior Labs 為核心在歐洲建立 Frontier 級別 AI 研究機構，Prior Labs 以獨立實體形式繼續運作，交易預計在 Q2 或 Q3 完成，TechCrunch 確認交易規模約 11.6 億美元（SAP 內部代號「NemoClaw」）。Prior Labs 由機器學習教授 Frank Hutter、Noah Hollmann 及 Sauraj Gambhir 於 2024 年末創立，總部德國弗萊堡，成立約 18 個月，研究人員來自 Google、Microsoft、Amazon、Jane Street 及 CERN。核心技術 TabPFN（Tabular Prior-data Fitted Networks）是以企業結構化表格資料為對象的基礎模型，可在單次前向傳遞中完成分類與回歸，無需任務特定訓練，在數百項學術研究中匹敵調參梯度提升模型（XGBoost、LightGBM），研究發表於 Nature 期刊，開源版本累計逾 300 萬次下載。</p><p><strong>第二</strong>　SAP 此案的戰略核心是對 LLM 為主的企業 AI 競爭路線的主動差異化。SAP 系統每年處理全球 87% 的商業交易記錄，這些資料的絕大多數是表格型（ERP 訂單、庫存流、供應商付款、客戶流失），而非文字；TabPFN 在此類資料上的零訓練推理效率遠超 GPT 系列，是 SAP 在與 Microsoft Copilot（整合 GPT）和 Salesforce Einstein（整合 OpenAI）的競爭中，選擇在算法層建立非 LLM 護城河的技術賭注。從地緣角度，此案是歐洲近年最具規模的本土 Frontier AI 投資之一，打破「歐洲 AI 無頂尖研究群」的固有敘事，Prior Labs 研究密度在結構化 AI 子領域具全球競爭力。NemoClaw 代號暗示與 NVIDIA Nemotron Coalition 框架的潛在整合路線，值得後續追蹤。</p><p><strong>第三</strong>　對企業 CIO 而言，TabPFN 在無需微調的條件下達到與調參模型相當的預測精準度，若 Prior Labs 在 SAP 資源投入後推出 Enterprise API，建議在 H2 2026 的 ERP AI 模組評估中重點驗證採購延遲預測、庫存優化及客戶流失率三個高頻業務場景的推理效能，這三項是判斷 TabPFN 投資報酬率的直接業務錨點。對 BEXS 學員而言，SAP（$SAP、XETRA 上市）以歐洲 Frontier AI Lab 框架重新定位技術能力敘事，若後續財報中 AI 模組滲透率出現量化提升，是重估 SAP 技術溢價的直接觸發點，建議在 H2 2026 財報中追蹤 AI 雲端模組 ARR 增速。對開發者而言，TabPFN 開源版本在 SAP 支援下的迭代加速，對結構化資料的 AutoML、企業數位孿生及時間序列場景均有高相關性，是評估是否從梯度提升遷移至 TabPFN 架構的重要技術信號，建議在 H2 2026 跟蹤 Prior Labs 開源更新頻率。</p>"
    }
]

with open(PULSE_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

existing_urls = {item["url"] for item in data.get("items", [])}

items_to_add = [item for item in new_items if item["url"] not in existing_urls]

if not items_to_add:
    print("NO_NEW_ITEMS")
    sys.exit(0)

data["items"] = items_to_add + data.get("items", [])
data["items"] = data["items"][:30]
data["updated_at"] = "2026-05-23T08:10:00+08:00"

with open(PULSE_PATH, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"ADDED:{len(items_to_add)}")
