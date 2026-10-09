import os
from crewai import Agent, Crew, Process, Task, LLM

# --------------------------------------------------
# 金鑰與 API Base 設定 (OpenRouter + DeepSeek)
# --------------------------------------------------
openrouter_api_key = os.getenv("OPENROUTER_API_KEY")

if openrouter_api_key:
    os.environ["OPENAI_API_KEY"] = openrouter_api_key
    os.environ["OPENAI_API_BASE"] = "https://openrouter.ai/api/v1"

llm = LLM(
    model="openrouter/deepseek/deepseek-chat",
    base_url="https://openrouter.ai/api/v1",
    api_key=openrouter_api_key,
    temperature=0.1
)

class InternationalTradeLegalDocumentAutomation:
    def __init__(self):
        # Agent 1: 關務法規研究員
        self.legal_researcher = Agent(
            role="國際貿易法規與關務研究員",
            goal="針對進出口國家、產品類別及 HS Code 檢索最新海關法規、貿易條約、關稅及合規要求",
            backstory="你是一位精通國際貿易法、海關申報與國際進出口規管條款的資深法規顧問。",
            verbose=True,
            allow_delegation=False,
            llm=llm
        )

        # Agent 2: 進口商 (買家) 信用與誠信風險盡職調查專家
        self.credit_risk_assessor = Agent(
            role="進口商 (買家) 信用與誠信風險盡職調查專家",
            goal="針對進口商 (買家) 之企業識別訊息進行公開數據搜查，完成獨立的信用度與誠信風險評估",
            backstory="你是一位資深的國際商業徵信與合規審查專家，專門針對全球買家/進口商企業進行法律訴訟、監管違規、制裁名單篩查、破產清盤、海關違規、負面新聞、公司狀態及高管紀錄進行盡職調查與風險評級。",
            verbose=True,
            allow_delegation=False,
            llm=llm
        )

        # Agent 3: 國際貿易法律文件與風險報告撰寫專家
        self.document_writer = Agent(
            role="國際貿易法律文件與風險報告撰寫專家",
            goal="根據交易資訊、關務法規及買家信用風險評估結果，生成完全無佔位符、無 'REQUIRES COMPLETION'、包含三大核心部分的完整中英雙語專業法律文件",
            backstory="你是一位頂尖的國際商務律師，擅長撰寫符合國際慣例（Incoterms 2020）且兼具風險提示與買方信用評估的全中英雙語商業合約與報告。",
            verbose=True,
            allow_delegation=False,
            llm=llm
        )

    def kickoff(self, inputs: dict) -> str:
        # Task 1: 關務法規搜查
        research_task = Task(
            description=(
                "請針對以下貿易背景進行海關法規與合規分析：\n"
                "- 文件類型: {document_type}\n"
                "- 目標進口國: {target_import_country} | HS Code: {hs_code}\n"
                "- 生產地: {place_of_production} | 卸貨港: {port_of_discharge} | 貿易術語: {incoterm}\n"
                "請列出相關進出口海關申報注意事項、可能面臨的特別關稅/關稅率及主要合規條款。"
            ),
            expected_output="一份包含關務法規、HS Code 申報注意事項及海關合規條款的摘要報告。",
            agent=self.legal_researcher
        )

        # Task 2: 進口商 (買家) 信用及誠信風險評估 (僅針對買家)
        credit_risk_task = Task(
            description=(
                "請【僅針對進口商 (買家)】進行企業信用與誠信風險盡職調查評估：\n\n"
                "【進口商 (買家) 識別資料】\n"
                "- 公司名稱: {importer_company_name}\n"
                "- 註冊號碼: {importer_reg_no} | 稅號: {importer_tax_id}\n"
                "- 公司地址: {importer_address}\n"
                "- 聯絡電話: {importer_phone} | 電郵: {importer_email}\n"
                "- 授權代表: {importer_auth_rep} ({importer_auth_rep_title})\n\n"
                "【評估類別 (針對進口商以下 8 大範疇進行獨立分析與核實)】：\n"
                "1. 🏛️ 法律訴訟紀錄（民事、刑事、商業爭議）\n"
                "2. ⚖️ 監管違規紀錄（罰款、執法行動、牌照撤銷）\n"
                "3. 🚨 制裁名單篩查（OFAC、EU、UN、HK、UK 制裁名單）\n"
                "4. 💸 破產 / 清盤紀錄（無力償債、清盤/破產保護申請）\n"
                "5. 🛃 海關違規紀錄（走私、出口管制違規、關稅逃避）\n"
                "6. 📰 負面新聞（詐騙指控、付款違約、消費者投訴）\n"
                "7. 🏢 公司註冊狀態（仍在運作 / 已解散 / 已被撤銷）\n"
                "8. 👤 董事 / 高管不良紀錄（授權代表相關背景）\n\n"
                "【風險評級制度】：\n"
                "- ✅ LOW — 未發現負面紀錄\n"
                "- ⚠️ MEDIUM — 有需要注意但非決定性的紀錄\n"
                "- 🔴 HIGH — 存在重大風險紀錄\n"
                "- ❓ INSUFFICIENT DATA — 搜查無結果或資料不足，建議獨立核實\n\n"
                "【重要說明】：評估需完全基於公開資料。若搜查無結果或因公開檢索限制未能獲取即時數據，必須明確標示為 INSUFFICIENT DATA，並詳細列出簽約前針對買家的獨立核實建議與風險控制措施。"
            ),
            expected_output="一份包含進口商 (買家) 8 大範疇獨立評估、綜合風險評級（LOW/MEDIUM/HIGH/INSUFFICIENT DATA）及建議行動的信用與誠信風險評估報告。",
            agent=self.credit_risk_assessor
        )

        # Task 3: 起草並合併完整三合一法律文件
        write_document_task = Task(
            description=(
                "請嚴格根據表單輸入資料、關務研究與進口商信用風險評估結果，起草並輸出【完整合併為一份】的最終法律文件。文件必須包含以下三個主要部分（全中英雙語逐段/逐句對照）：\n\n"
                "【第一部分：合約 / 文件正文 [Contract / Main Document Body]】\n"
                "- 包含雙方完整主體資料、商品描述、數量、單價、總價、Incoterms 2020、付款條件、銀行資料、保固期、準據法與爭議解決、簽署區。\n"
                "- 嚴禁出現 '[Date]', '[Name]', '[Address]', 'REQUIRES COMPLETION' 或 '[REQUIRES COMPLETION]' 等任何佔位符！\n\n"
                "【第二部分：=== RISK ADVISORY / 風險建議 ===】\n"
                "- 針對付款與財務風險、海關與關稅風險、交付與物流風險、知識產權風險、法律管轄風險、監管合規風險、違規補救風險等進行詳細分析與具體緩解措施說明。\n\n"
                "【第三部分：=== CREDIT & INTEGRITY RISK ASSESSMENT / 信用及誠信風險評估 ===】\n"
                "- 結構包含：\n"
                "  1. 進口商 (買家) 信用及誠信風險評估 (SECTION 1: IMPORTER CREDIT & INTEGRITY ASSESSMENT)，針對 8 大類別（法律訴訟、監管違規、制裁名單、破產清盤、海關違規、負面新聞、公司註冊狀態、董事/高管紀錄）明確標示風險評級（如 INSUFFICIENT DATA 或相應級別）。\n"
                "  2. 整體買方交易風險裁定 (SECTION 2: OVERALL BUYER RISK VERDICT)，含綜合風險水平與主要風險標誌（Key Risk Flags）。\n"
                "  3. 簽約前針對買家之建議盡職調查步驟 (Recommended Buyer Due Diligence Actions)。\n\n"
                "【鐵律指令】：\n"
                "1. 全文件（三大部分）每一個章節標題、條款內文、表格與報告內容均必須採取【全中英雙語對照】（英文在上，繁體中文在下）。\n"
                "2. 格式使用標準 Markdown，包含 Markdown 表格與粗體標題。"
            ),
            expected_output="一份包含合約正文、風險建議報告及買家信用與誠信風險評估報告的三合一完整 Markdown 格式雙語法律文件。",
            agent=self.document_writer
        )

        # 組成 Crew 執行
        crew = Crew(
            agents=[self.legal_researcher, self.credit_risk_assessor, self.document_writer],
            tasks=[research_task, credit_risk_task, write_document_task],
            process=Process.sequential,
            verbose=True
        )

        result = crew.kickoff(inputs=inputs)
        return str(result)

def run_flow(inputs: dict) -> str:
    automation = InternationalTradeLegalDocumentAutomation()
    return automation.kickoff(inputs)