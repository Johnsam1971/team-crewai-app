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
        # 1. 定義 Agent
        self.legal_researcher = Agent(
            role="國際貿易法規研究員",
            goal="針對特定進出口國家、產品類別及 HS Code 檢索最新法規、條約與條款合規要求",
            backstory="你是一位精通國際貿易法、海關法規與各國進出口標準的資深法律顧問。",
            verbose=True,
            allow_delegation=False,
            llm=llm
        )

        self.document_writer = Agent(
            role="國際貿易法律文件撰寫專家",
            goal="根據用戶輸入的具體交易資訊，生成完全無佔位符、無 'REQUIRES COMPLETION'、可直接簽署的完整中英雙語專業法律文件",
            backstory="你是一位頂尖的國際商務律師，擅長撰寫精確、無漏洞且符合國際慣例（如 Incoterms 2020）的全中英雙語對照商業合約與貿易文件。",
            verbose=True,
            allow_delegation=False,
            llm=llm
        )

    def kickoff(self, inputs: dict) -> str:
        # Task 1: 貿易合規研究
        research_task = Task(
            description=(
                "請針對以下貿易背景進行法律與合規分析：\n"
                "- 文件類型: {document_type}\n"
                "- 目標進口國: {target_import_country} | HS Code: {hs_code}\n"
                "- 生產地: {place_of_production} | 卸貨港: {port_of_discharge} | 貿易術語: {incoterm}\n"
                "請摘要列出寫入該文件時必須包含的核心條款與合規注意事項。"
            ),
            expected_output="一份包含該貿易行為核心合規要求與必備法律條款的清單摘要。",
            agent=self.legal_researcher
        )

        # Task 2: 撰寫全中英雙語法律文件
        write_document_task = Task(
            description=(
                "請嚴格根據以下提供的【實際交易資料】與研究結果，撰寫一份極度專業、完整的【全中英雙語對照】{document_type}：\n\n"
                "【合同基本資訊】\n"
                "- 合同編號: {contract_no}\n"
                "- 簽署日期: {contract_date}\n"
                "- 生效日期: {effective_date}\n\n"
                "【出口商 / 賣方】\n"
                "- 公司名稱: {exporter_company_name}\n"
                "- 地址: {exporter_address}\n"
                "- 註冊號碼: {exporter_reg_no} | 稅號: {exporter_tax_id}\n"
                "- 聯絡人: {exporter_contact_title} / {exporter_contact_name}\n"
                "- 電話: {exporter_phone} | 電子郵件: {exporter_email}\n"
                "- 授權代表: {exporter_auth_rep} ({exporter_auth_rep_title})\n\n"
                "【進口商 / 買方】\n"
                "- 公司名稱: {importer_company_name}\n"
                "- 地址: {importer_address}\n"
                "- 註冊號碼: {importer_reg_no} | 稅號: {importer_tax_id}\n"
                "- 聯絡人: {importer_contact_title} / {importer_contact_name}\n"
                "- 電話: {importer_phone} | 電子郵件: {importer_email}\n"
                "- 授權代表: {importer_auth_rep} ({importer_auth_rep_title})\n\n"
                "【商品與價格】\n"
                "- 商品名稱: {product_name}\n"
                "- 詳細描述: {product_description}\n"
                "- 數量: {product_qty} | 單價: {unit_price} {currency} | 總價: {total_price} {currency}\n"
                "- 產品規格: {product_specs}\n"
                "- 包裝方式: {product_packaging}\n\n"
                "【運輸與支付條件】\n"
                "- 生產地: {place_of_production} | 卸貨港: {port_of_discharge}\n"
                "- 預計生產日: {production_date} | 預計交貨日: {delivery_date}\n"
                "- Incoterms: {incoterm} | 付款方式: {payment_method}\n"
                "- 付款時機: {payment_timing}\n"
                "- 銀行帳戶資料: {bank_details}\n"
                "- 保固期: {warranty_period} | 準據法: {governing_law} | 爭議解決: {dispute_resolution}\n"
                "- 分批裝運: {partial_shipment}\n\n"
                "【鐵律指令 - 必須絕對執行】\n"
                "1. 【全中英雙語對照鐵律】：文件中每一個章節標題、所有條款內文、表格內容、雙方責任義務、聲明事項以及末尾的《風險評估與建議報告 (Risk Advisory Report)》，均必須採用【逐段/逐句的中英雙語對照】（英文在上，繁體中文在下，或段落並列）。絕不可只寫雙語標題而內文留為純英文！\n"
                "2. 必須將上述所有實際資料精確寫入文件中，嚴禁輸出任何 '[Date]', '[Name]', '[Address]', 'REQUIRES COMPLETION' 或 '[REQUIRES COMPLETION]' 等佔位符！\n"
                "3. 若有未填寫的次要條款（如具體銀行 SWIFT 碼或細節號碼），請根據國際商業慣例直接補充合理的正式內容，絕不可以留空。\n"
                "4. 結構必須完整包含：雙語合約標題、雙方主體資訊、正式條款（Parties, Goods, Price, Delivery, Payment, Warranty, Governing Law, Signatures）以及末尾附帶的全雙語《風險評估與建議報告 (Risk Advisory Report)》。\n"
                "5. 格式使用標準 Markdown，包含 Markdown 表格（用於商品單價與總價對照）與粗體標題。"
            ),
            expected_output="一份內容完整、已填入所有實體資料、無任何佔位符、內文全面實施中英雙語對照的可直接簽署 Markdown 格式法律文件。",
            agent=self.document_writer
        )

        # 4. 組成 Crew 並執行
        crew = Crew(
            agents=[self.legal_researcher, self.document_writer],
            tasks=[research_task, write_document_task],
            process=Process.sequential,
            verbose=True
        )

        result = crew.kickoff(inputs=inputs)
        return str(result)

def run_flow(inputs: dict) -> str:
    automation = InternationalTradeLegalDocumentAutomation()
    return automation.kickoff(inputs)