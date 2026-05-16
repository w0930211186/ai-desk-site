#!/usr/bin/env python3
import json, sys

PULSE_PATH = "/home/user/ai-desk-site/data/pulse.json"

new_items = [
    {
        "id": "pulse-2026-05-16-10-recursive-superintelligence-650m",
        "ts": "2026-05-16T10:00:00+08:00",
        "title": "Recursive Superintelligence 以 6.5 億美元出關・Google 風投與 Nvidia 同押「自我遞迴改進 AI」實驗室",
        "source": "TechCrunch",
        "url": "https://techcrunch.com/2026/05/14/what-happens-when-ai-starts-building-itself/",
        "blurb": "Richard Socher 與前 Google DeepMind 科學家 Tim Rocktäschel 共同創辦的 Recursive Superintelligence 5 月 13 日出關，以 46.5 億美元估值完成 6.5 億美元融資，Google 風投 GV、Nvidia 及 AMD 同輪跟投；不足 30 人團隊，使命是打造無需人類介入即可自我遞迴改進的 AI 系統，Level 1 自主訓練系統預計 2026 年中公開。",
        "editorial": "<p><strong>第一</strong>2026 年 5 月 13 日，英國 AI 新創 Recursive Superintelligence 宣布從隱形期公開出關，同步披露完成 6.5 億美元融資，估值達 46.5 億美元。本輪由 Google 風投 GV 及 Greycroft 領投，Nvidia 與 AMD 同輪跟投。公司聯合創辦人為 Richard Socher（執行長，前 Salesforce 首席科學家、you.com 創辦人）及 Tim Rocktäschel（前 Google DeepMind 科學家、UCL 人工智能教授），核心團隊不足 30 人，成員分別來自 Meta 及 OpenAI。Recursive Superintelligence 以倫敦為基地，成立時間僅數月，核心論點是：現有 AI 系統在訓練結束後即靜止，而真正的智慧增強需要系統能在無人類介入的前提下，透過分析自身表現持續遞迴改進，擺脫以人類偏好標注作為瓶頸的 RLHF 依賴。公司計畫於 2026 年中推出「Level 1 自主訓練系統」公開版本。</p><p><strong>第二</strong>Recursive 的架構主張在哲學上與 DeepMind AlphaZero 的自我對弈設計一脈相承，但試圖在開放領域（非封閉博弈空間）中實現類似的自我最佳化機制，技術挑戰量級顯著更高。從資本結構解讀，GV（Google 風投）、Nvidia 及 AMD 同時出現在同一輪，代表的不僅是財務押注，更是生態系綁定——Recursive 的自主訓練迴路若成立並需要大量計算，其晶片採購優先序將直接影響 GPU 供應商的份額競逐；Nvidia 與 AMD 同步下注，暗示雙方均不願讓這個潛在的大型計算消費者落入單一陣營。從競爭格局看，Recursive 是 Ineffable Intelligence（前 DeepMind RL 部門負責人 David Silver 創辦，估值 51 億美元）之後，2026 年第二家以「去 RLHF、自主學習」論點完成超大規模融資的英國 AI 實驗室，標誌倫敦在 ASL-3 以上研究賽道的資本吸引力已形成正向循環。</p><p><strong>第三</strong>對開發者而言，「Level 1 自主訓練」的技術定義與 API 開放時程是 2026 年下半年最值得追蹤的 AI 架構動態之一；若 Recursive 公開評估基準，其自我改進能力的客觀量測方法本身就將成為推論能力評估框架的重要補充。對企業 CIO 而言，Recursive 目前仍處研究階段，短期採購價值有限；但團隊密度與資本規模的組合預示其商業化速度可能超出預期，建議納入 18 個月技術雷達追蹤清單，重點觀察 2026 年底前的概念驗證發布。對 BEXS 學員而言，Nvidia 與 AMD 同步參與 Recursive 融資是觀察兩家 GPU 廠商在「自主學習 AI 基礎設施」賽道最新競合動態的直接信號；若 Level 1 自主訓練系統在年底前完成驗證，其算力需求規模將成為判斷下一輪高端 GPU 及 HBM 採購週期的先行指標。</p>"
    },
    {
        "id": "pulse-2026-05-16-10-sap-prior-labs-tabular-foundation-model",
        "ts": "2026-05-16T10:00:00+08:00",
        "title": "SAP 十億歐元收購德國 Prior Labs・押注表格基礎模型（TFM）成為結構化資料 AI 的歐洲標準",
        "source": "SAP Newsroom",
        "url": "https://news.sap.com/2026/05/sap-to-acquire-prior-labs-establish-frontier-ai-lab-europe/",
        "blurb": "SAP 宣布收購弗萊堡 AI 新創 Prior Labs，四年承諾注入逾十億歐元打造歐洲前沿 AI 實驗室；Prior Labs 的表格基礎模型 TabPFN 已發表於 Nature 並刷新數百項學術基準，是歐洲最大企業軟體廠商在 LLM 主流之外，選擇以結構化資料專用架構建立核心 AI 能力的明確宣示。",
        "editorial": "<p><strong>第一</strong>2026 年 5 月 4 日，SAP SE 與德國 AI 新創 Prior Labs 宣布簽署確定性收購協議，具體收購金額未披露。SAP 承諾未來四年投入逾十億歐元，支持 Prior Labs 在保持獨立運營的前提下擴展為「全球領先的結構化資料前沿 AI 實驗室」。交易預計於 2026 年第二或第三季完成，待監管審批。Prior Labs 由機器學習教授 Frank Hutter、Noah Hollmann 及 Sauraj Gambhir 共同創立，總部位於德國弗萊堡，在柏林及紐約另設辦公室，核心研究人員分別來自 Google、Apple、Amazon、Microsoft、Jane Street 及 CERN。Prior Labs 的核心技術成果是 TabPFN 系列表格基礎模型（Tabular Foundation Models, TFM）——專為結構化資料（如 ERP 交易記錄、財務資料表、供應鏈資料庫）設計的基礎模型架構；TabPFN 論文已發表於 Nature，在數百項獨立學術研究的表格資料基準測試中達到業界最高水準。</p><p><strong>第二</strong>SAP 此次收購的核心論點是「結構化資料才是企業 AI 的真正戰場」。當前 AI 主流敘事以大型語言模型為中心，然而 SAP 系統中流通的核心企業資料——應付帳款、庫存水位、客戶流失預測、供應商風險評分——幾乎全部是表格形式，LLM 在此類任務的表現遠低於專用 TFM。Prior Labs 的 TabPFN 在少樣本學習與零樣本類比方面的性能，使其能在幾乎無需微調的前提下直接處理企業資料預測任務。從歐洲 AI 競爭格局看，SAP 此舉是歐洲最大科技公司在「不押注通用 LLM 競賽」前提下建立核心 AI 能力的最直接宣示；TFM 的決策邏輯相較 LLM 更具可解釋性，亦符合 EU AI Act 對金融、醫療等高監管行業在可解釋性方面的合規要求，為「合規友好型 AI」路線提供商業支撐。</p><p><strong>第三</strong>對企業 CIO 而言，TabPFN 系列的商業化落地意味著 SAP 客戶在 2026 下半年有望在 SAP 原生環境中直接調用 TFM 能力進行業務預測；評估此路線的核心前提是：現有 SAP ERP 資料倉儲的清洗程度是否足以支撐 TFM 推論，資料治理團隊應提前介入評估。對開發者而言，Prior Labs 的 TabPFN 模型已部分開源，可在 Hugging Face 取得；在收購完成前建議優先評估開源版本在企業結構化資料場景的適用性，以建立技術判斷基礎。對 BEXS 學員而言，SAP（NYSE: SAP）以十億歐元級別強化 AI 基礎研究能力，是傳統企業軟體廠商在 AI 轉型週期中防禦性卡位的典型動作；相似邏輯下，Salesforce、Oracle、ServiceNow 在結構化資料 AI 的投資路線值得同步追蹤，以判斷企業 AI 生態系在 LLM 主流與 TFM 專用路線之間的聚合或分化走向。</p>"
    },
    {
        "id": "pulse-2026-05-16-10-anthropic-agent-sdk-billing-split",
        "ts": "2026-05-16T10:00:00+08:00",
        "title": "Anthropic 六月十五日起拆出代理 SDK 計費池・吃到飽 AI 訂閱在 Agentic 浪潮下正式終止",
        "source": "Axios",
        "url": "https://www.axios.com/2026/05/14/anthropic-claude-price-openai-tokens",
        "blurb": "Anthropic 宣布自 2026 年 6 月 15 日起，Claude Agent SDK、claude -p 及第三方代理框架的程式化用量從訂閱限額池拆出，改以 API 正價計費；Pro 每月額度僅 20 美元封頂，重度代理用戶實質成本漲幅估達 12 至 175 倍，宣告「AI 吃到飽訂閱」時代在代理工作流場景下的終結。",
        "editorial": "<p><strong>第一</strong>Anthropic 於 2026 年 5 月 13 日向 Max 20x 訂閱用戶發送電郵，宣布自 6 月 15 日起，透過 Claude Agent SDK、claude -p、GitHub Actions 及第三方代理框架進行的所有程式化用量，將從原有訂閱速率限額池拆出，移入獨立的月度代理額度池，並按標準 API 報價計費。新制下月度代理額度依訂閱等級設定：Pro（月費 20 美元）獲 20 美元額度、Max 5x（月費 100 美元）獲 100 美元額度、Max 20x（月費 200 美元）獲 200 美元額度；額度耗盡後需另購，不可使用互動用量剩餘額度補位，且不跨月結轉。此調整直接導火線是以 OpenClaw 為代表的第三方代理框架「訂閱套利」問題——部分用戶以每月 20 至 200 美元訂閱驅動數千美元的代理用量。根據開發者社群分析，以標準 API 報價換算，重度代理用戶的等效成本漲幅介於 12 至 175 倍。</p><p><strong>第二</strong>此計費拆分是 AI 訂閱商業模式在代理工作流浪潮下的結構性斷裂。Frontier lab 的訂閱定價邏輯建立在「人類每小時能消費的 token 量有上限」的假設之上；代理工作流可以每秒觸發數十次工具調用，一個持續運行的代理迴路在數分鐘內即可耗盡設計為「月度人類用量」的配額。Anthropic 此舉等同正式承認代理場景與互動場景是截然不同的商業模式，訂閱池與 API 計費的分離是必然結果，而非政策失誤。從競爭格局看，OpenAI 的 Codex 代理計畫（Pro 計畫無限額）與 Anthropic 的新計費結構形成直接對比——在爭奪開發者採用的當口，訂閱策略的差異化將成為代理框架廠商選邊的重要參數，長期而言代理場景的計費模型最終將趨向「用量付費」，訂閱包月只是過渡型態。</p><p><strong>第三</strong>對開發者而言，6 月 15 日前的關鍵行動是稽核現有代理工作流的月度 token 消耗，計算在新計費結構下的等效成本，並評估是否需要轉向直接 API 呼叫或優化代理迴路的 token 效率；Zed、MindStudio 等集成 Claude Agent SDK 的第三方工具亦已發布因應指南，應在更新前確認工具鏈定價影響。對企業 CIO 而言，此變化要求重新評估「AI 助手訂閱」與「AI 代理工作流」的採購框架——兩者的成本結構、使用模式與供應商協議設計應明確分開，避免預算低估。對 BEXS 學員而言，Anthropic 代理計費的結構調整是觀察其在 agent 時代商業模式成熟度的重要信號；若此「互動訂閱 + 代理計量」雙軌模式在業界複製，AI 訂閱企業的年化收入增速計算應加入「代理用量轉化率」作為新的核心變數。</p>"
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
data["updated_at"] = "2026-05-16T10:00:00+08:00"

with open(PULSE_PATH, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"ADDED:{len(items_to_add)}")
