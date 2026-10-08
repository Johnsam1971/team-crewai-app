import os
import sys
import streamlit as st

# 將 src 目錄納入 Python 模組搜尋路徑
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from international_trade_legal_document_automation.crews.crew import InternationalTradeLegalDocumentAutomation

# 頁面配置
st.set_page_config(
    page_title="國際貿易自動化文件與風險分析系統",
    page_icon="⚖️",
    layout="wide"
)

st.title("⚖️ 國際貿易自動化文件與風險分析系統")
st.markdown("填寫下方交易與合約資訊，AI Agent 團隊將為您自動生成**中英文專業貿易文件**及**風險評估建議報告**。")

# 獲取 API Key（優先讀取 secrets，其次讀取環境變數）
openrouter_key = None
try:
    openrouter_key = st.secrets.get("OPENROUTER_API_KEY")
except Exception:
    pass

if not openrouter_key:
    openrouter_key = os.getenv("OPENROUTER_API_KEY")

# 側邊欄輸入框
with st.sidebar:
    st.header("🔑 API 設定")
    sidebar_key = st.text_input("輸入 OpenRouter API Key：", value=openrouter_key or "", type="password")
    if sidebar_key:
        openrouter_key = sidebar_key

# 只有在完全沒有 API Key 時才顯示黃色警告框
if not openrouter_key:
    st.warning("⚠️ 未檢測到 OPENROUTER_API_KEY，請於側邊欄輸入後按 Enter 確認。")
else:
    # 成功取得 Key 後同步寫入環境變數
    os.environ["OPENROUTER_API_KEY"] = openrouter_key
    os.environ["OPENAI_API_KEY"] = openrouter_key
    os.environ["OPENAI_BASE_URL"] = "https://openrouter.ai/api/v1"

st.subheader("📋 Run Parameters / 交易資料表單")

# 使用 5 個分頁整理所有必要欄位
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "1. 文件與通關資訊", 
    "2. 出口商資料 (Exporter)", 
    "3. 進口商資料 (Importer)", 
    "4. 產品細節 (Product)", 
    "5. 貿易與付款條款 (Terms)"
])

with tab1:
    col1, col2 = st.columns(2)
    with col1:
        document_type = st.selectbox(
            "document_type *",
            [
                "Sales Contract",
                "Commercial Invoice",
                "Packing List",
                "Certificate of Origin",
                "LC Application",
                "Bill of Lading",
                "Inspection Certificate",
                "Other"
            ],
            help="Select the type of trade document to generate. Enter exactly one of the options."
        )
        target_import_country = st.text_input(
            "target_import_country *", 
            "United States", 
            help="Country where goods will be imported.\nExamples: United States | Germany | Japan | Australia | United Kingdom | France | Canada"
        )
        place_of_production = st.text_input(
            "place_of_production *", 
            "CHINA", 
            help="Country or city where goods are manufactured.\nExamples: CHINA | VIETNAM | TAIWAN | HONG KONG | THAILAND | MALAYSIA"
        )
    with col2:
        hs_code = st.text_input(
            "hs_code *", 
            "5603.93", 
            help="Harmonized System Code for customs classification. Enter the full HS code including dots.\nExamples: 8471.30 | 6203.42 | 9403.20 | 8516.60 | 5603.93"
        )
        port_of_discharge = st.text_input(
            "port_of_discharge *", 
            "Los Angeles", 
            help="Port where goods will be unloaded at destination.\nExamples: Los Angeles | Hamburg | Yokohama | Rotterdam | Sydney | New York | Tokyo"
        )
        output_language = st.selectbox(
            "文件語言版本", 
            ["中英文雙語對照版 (Bilingual CN/EN)", "僅英文 (English Only)", "僅中文 (Traditional Chinese Only)"],
            help="選擇輸出的報告與文件語言格式。"
        )

with tab2:
    st.markdown("#### Exporter Information")
    ex_col1, ex_col2 = st.columns(2)
    with ex_col1:
        exporter_company_name = st.text_input(
            "company_name (Exporter)", 
            "ABC Technology Limited",
            help="Full legal registered company name of exporter.\nExample: ABC Manufacturing Ltd. | ABC Technology Limited"
        )
        exporter_address = st.text_area(
            "address (Exporter)", 
            "Room 1201, 12/F, ABC Tower, Shatin, Hong Kong", 
            height=68,
            help="Full registered address including street, city, country.\nExample: 123 Industrial Road, Shenzhen, Guangdong, China 518000"
        )
        exporter_tax_id = st.text_input(
            "tax_id (Exporter)", 
            "186432220-001",
            help="Tax identification / VAT / GST number.\nExample: 91440300MA5DXXXX00 | GB123456789 | 186432220-001"
        )
        exporter_company_reg = st.text_input(
            "company_registration_no (Exporter)", 
            "186432220-001",
            help="Company registration or business license number.\nExample: 91440300MA5DXXXX00"
        )
    with ex_col2:
        exporter_contact_title = st.text_input(
            "contact_title (Exporter)", 
            "Director David Wong",
            help="Contact person title and full name.\nExample: Mr. John Smith | Ms. Mary Chan | Director David Wong | Sales Manager"
        )
        exporter_contact_email = st.text_input(
            "contact_email (Exporter)", 
            "john@abc.com.hk",
            help="Contact email address.\nExample: john.smith@abcmfg.com | john@abc.com.hk"
        )
        exporter_contact_phone = st.text_input(
            "contact_phone (Exporter)", 
            "+852 91234567",
            help="Contact phone with country code.\nExample: +86-755-12345678 | +852-21234567 | +1-213-5551234"
        )
        exporter_auth_rep = st.text_input(
            "authorized_representative (Exporter)", 
            "Johnson",
            help="Full name of authorized signatory.\nExample: John Smith | Johnson"
        )
        exporter_auth_rep_title = st.text_input(
            "authorized_rep_title (Exporter)", 
            "CEO",
            help="Title of authorized signatory.\nExample: General Manager | Director | CEO"
        )

with tab3:
    st.markdown("#### Importer Information")
    im_col1, im_col2 = st.columns(2)
    with im_col1:
        importer_company_name = st.text_input(
            "company_name (Importer)", 
            "DP Limited",
            help="Full legal registered company name of importer.\nExample: XYZ Trading Inc. | DP Limited"
        )
        importer_address = st.text_area(
            "address (Importer)", 
            "6925 Century Avenue, Suite 700 Mississauga, Ontario, L5A 0E3, Canada", 
            height=68,
            help="Full registered address including street, city, country.\nExample: 456 Commerce Street, Los Angeles, CA 90001, USA"
        )
        importer_tax_id = st.text_input(
            "tax_id (Importer)", 
            "12-3456789",
            help="Tax identification / VAT/GST / importer number.\nExample: 12-3456789 | DE123456789 | AU12345678"
        )
        importer_company_reg = st.text_input(
            "company_registration_no (Importer)", 
            "TF-123456789",
            help="Company registration or importer identification number.\nExample: US-EIN-12-3456789 | DE-HRB-123456 | TF-123456789"
        )
    with im_col2:
        importer_contact_title = st.text_input(
            "contact_title (Importer)", 
            "Purchasing Manager",
            help="Contact person title and full name.\nExample: Mr. Robert Lee | Ms. Sarah Johnson | Manager Tom Brown | Purchasing Manager"
        )
        importer_contact_email = st.text_input(
            "contact_email (Importer)", 
            "John@dp.com",
            help="Contact email address.\nExample: robert.lee@xyztrading.com | John@dp.com"
        )
        importer_contact_phone = st.text_input(
            "contact_phone (Importer)", 
            "1-800-931-3456",
            help="Contact phone with country code.\nExample: +1-213-5559876 | +49-30-12345678 | +81-3-12345678"
        )
        importer_auth_rep = st.text_input(
            "authorized_representative (Importer)", 
            "Robert",
            help="Full name of authorized signatory.\nExample: Robert Lee | Robert"
        )
        importer_auth_rep_title = st.text_input(
            "authorized_rep_title (Importer)", 
            "Director",
            help="Title of authorized signatory.\nExample: President | Purchasing Manager | Director"
        )

with tab4:
    st.markdown("#### Product Details")
    p_col1, p_col2 = st.columns(2)
    with p_col1:
        product_name = st.text_input(
            "name *", 
            "GeoTextile VIP1230",
            help="Full product name and model/type.\nExample: Wireless Bluetooth Headphones Model BT-500 | Wooden Office Chair Type A | GeoTextile VIP1230"
        )
        currency = st.selectbox(
            "currency *", 
            ["USD", "EUR", "GBP", "JPY", "AUD", "CAD", "CNY", "HKD"],
            help="Transaction currency. Enter exactly one of the options."
        )
        quantity = st.text_input(
            "quantity *", 
            "100000 SQM",
            help="Quantity and unit of measure.\nExample: 500 PCS | 1000 UNITS | 200 SETS | 50 CARTONS | 100000 SQM"
        )
        unit_price = st.text_input(
            "unit_price *", 
            "2.50", 
            help="Unit price (numbers only, currency stated separately).\nExample: 45.00 | 128.50 | 350.00 | 2.50"
        )
        total_price = st.text_input(
            "total_price *", 
            "250000.00", 
            help="Total contract price (numbers only, currency stated separately).\nExample: 22500.00 | 64250.00 | 250000.00"
        )
    with p_col2:
        packaging = st.text_input(
            "packaging *", 
            "10 Rolls per carton, export standard carton 40x45x120cm, total 10000 cartons",
            help="Packaging details.\nExample: 10 PCS per carton, export standard carton 40x30x25cm, total 50 cartons"
        )
        production_date = st.text_input(
            "production_date *", 
            "2026-11", 
            help="Estimated or actual production date. Format: YYYY-MM or YYYY-MM-DD.\nExample: 2026-11 | 2026-11-15"
        )
        description = st.text_area(
            "description *", 
            "200 Meter 70 g/m2 nonwoven geotextile Jumbo Roll, 10 Rolls per Carton Boxes", 
            height=68,
            help="Detailed product description for customs and commercial documents.\nExample: Wireless stereo headphones with active noise cancellation, Bluetooth 5.0, rechargeable lithium battery"
        )
        specifications = st.text_area(
            "specifications *", 
            "Color: Black; Material: Nonwoven Geotextile 70g/m2", 
            height=68,
            help="Technical specifications, materials, dimensions, grade.\nExample: Material: ABS plastic + aluminum; Weight: 280g; Battery: 500mAh; Color: Black"
        )

with tab5:
    st.markdown("#### Trade Terms & Logistics")
    t_col1, t_col2 = st.columns(2)
    with t_col1:
        incoterm = st.text_input(
            "incoterm *", 
            "FOB Shenzhen Incoterms 2020",
            help="Incoterm rule, version and named place.\nExample: FOB Shenzhen Incoterms 2020 | CIF Los Angeles Incoterms 2020 | DAP Hamburg Incoterms 2020"
        )
        payment_method = st.text_input(
            "payment_method *", 
            "T/T 30% deposit, 70% before shipment",
            help="Payment method and terms.\nExample: T/T 30% deposit, 70% before shipment | Irrevocable LC at sight | D/P 60 days | Open Account 30 days"
        )
        payment_timing = st.text_input(
            "payment_timing", 
            "30% deposit within 7 days of contract signing, 70% balance before shipment",
            help="Payment schedule and due dates.\nExample: 30% deposit within 7 days of contract signing, 70% balance before shipment | Full payment by LC at sight"
        )
        inspection = st.text_input(
            "inspection *", 
            "No third-party inspection required",
            help="Inspection requirements, agency and timing.\nExample: SGS pre-shipment inspection at seller expense | Buyer inspection within 14 days of arrival | No third-party inspection required"
        )
        bank_details = st.text_input(
            "bank_details", 
            "Bank of China, Shenzhen Branch; A/C: 1234567890; SWIFT: BKCHCNBJ",
            help="Beneficiary bank name, account number, SWIFT code.\nExample: Bank of China, Shenzhen Branch; A/C: 1234567890; SWIFT: BKCHCNBJ | Leave blank if not yet determined"
        )
        governing_law = st.text_input(
            "governing_law *", 
            "Laws of Hong Kong",
            help="Governing law for the contract.\nExample: Laws of Hong Kong | Laws of England and Wales | Laws of Singapore | Laws of the People's Republic of China"
        )
        dispute_resolution = st.text_input(
            "dispute_resolution", 
            "Arbitration under HKIAC Rules, seat Hong Kong",
            help="Dispute resolution method, institution and seat.\nExample: Arbitration under HKIAC Rules, seat Hong Kong | ICC Arbitration, seat Singapore | CIETAC Beijing"
        )
    with t_col2:
        warranty_period = st.text_input(
            "warranty_period", 
            "14 days from date of received",
            help="Product warranty period.\nExample: 12 months from date of delivery | 2 years from date of manufacture | No warranty | 14 days from date of received"
        )
        partial_shipment = st.text_input(
            "partial_shipment", 
            "both allowed",
            help="Whether partial shipment and transshipment are permitted.\nExample: Partial shipment allowed, transshipment not allowed | Both allowed | Neither allowed"
        )
        estimated_production_date = st.text_input(
            "estimated_production_date", 
            "2026-11-01",
            help="Estimated production completion date. Format: YYYY-MM-DD or YYYY-MM.\nExample: 2026-11-01 | 2026-11"
        )
        estimated_delivery_date = st.text_input(
            "estimated_delivery_date", 
            "2026-12-01",
            help="Estimated delivery or shipment date. Format: YYYY-MM-DD or YYYY-MM.\nExample: 2026-12-01 | 2026-12"
        )

st.markdown("---")

# 觸發按鈕
if st.button(f"🚀 開始生成【{document_type}】文件與風險評估報告", type="primary", use_container_width=True):
    if not openrouter_key:
        st.error("請先提供 OpenRouter API Key！")
    else:
        with st.spinner(f"AI Agent 團隊正在處理【{document_type}】資料、進行條款風險分析，並起草中英文文件..."):
            try:
                # 構建傳遞給 CrewAI 的完整 Inputs 字典
                inputs = {
                    "document_type": document_type,
                    "target_import_country": target_import_country,
                    "hs_code": hs_code,
                    "language_requirement": output_language,
                    "place_of_production": place_of_production,
                    "port_of_discharge": port_of_discharge,
                    "topic": f"{document_type} for {product_name} ({output_language})",
                    
                    # Exporter 欄位
                    "exporter": {
                        "company_name": exporter_company_name,
                        "address": exporter_address,
                        "tax_id": exporter_tax_id,
                        "company_registration_no": exporter_company_reg,
                        "contact_title": exporter_contact_title,
                        "contact_email": exporter_contact_email,
                        "contact_phone": exporter_contact_phone,
                        "authorized_representative": exporter_auth_rep,
                        "authorized_rep_title": exporter_auth_rep_title
                    },
                    "exporter_name": exporter_company_name,
                    "exporter_address": exporter_address,
                    
                    # Importer 欄位
                    "importer": {
                        "company_name": importer_company_name,
                        "address": importer_address,
                        "tax_id": importer_tax_id,
                        "company_registration_no": importer_company_reg,
                        "contact_title": importer_contact_title,
                        "contact_email": importer_contact_email,
                        "contact_phone": importer_contact_phone,
                        "authorized_representative": importer_auth_rep,
                        "authorized_rep_title": importer_auth_rep_title
                    },
                    "importer_name": importer_company_name,
                    "importer_address": importer_address,
                    
                    # Product Details 欄位
                    "product_details": {
                        "name": product_name,
                        "currency": currency,
                        "quantity": quantity,
                        "unit_price": unit_price,
                        "total_price": total_price,
                        "packaging": packaging,
                        "description": description,
                        "specifications": specifications,
                        "production_date": production_date
                    },
                    "product_name": product_name,
                    "quantity": quantity,
                    "unit_price": unit_price,
                    "currency": currency,
                    "total_price": total_price,
                    
                    # Trade Terms 欄位
                    "trade_terms": {
                        "incoterm": incoterm,
                        "payment_method": payment_method,
                        "payment_timing": payment_timing,
                        "inspection": inspection,
                        "bank_details": bank_details,
                        "governing_law": governing_law,
                        "dispute_resolution": dispute_resolution,
                        "warranty_period": warranty_period,
                        "partial_shipment": partial_shipment,
                        "estimated_production_date": estimated_production_date,
                        "estimated_delivery_date": estimated_delivery_date
                    },
                    "incoterm": incoterm,
                    "payment_method": payment_method,
                    "governing_law": governing_law
                }

                # 執行 CrewAI 流程
                crew_instance = InternationalTradeLegalDocumentAutomation()
                result = crew_instance.crew().kickoff(inputs=inputs)

                # 檢查並手動拼接所有 Task 的輸出
                combined_outputs = []
                if hasattr(result, 'tasks_output') and result.tasks_output:
                    for task_out in result.tasks_output:
                        combined_outputs.append(str(task_out.raw))
                    result_text = "\n\n---\n\n".join(combined_outputs)
                else:
                    result_text = str(result)

                st.success(f"✨ 【{document_type}】文件與風險分析報告生成成功！")
                
                # 預覽區域：使用可拉動的 text_area 展示完整全文
                st.markdown("### 📄 文件內容與風險建議報告預覽")
                st.text_area("完整合約與報告內容", value=result_text, height=500)

                # 下載按鈕：確保傳入的 data 是完整的 UTF-8 編碼文本
                st.download_button(
                    label=f"📥 下載【{document_type}】完整中英文文件與報告 (.md)",
                    data=result_text.encode('utf-8'),
                    file_name=f"{document_type.replace(' ', '_')}_bilingual_report.md",
                    mime="text/markdown"
                )
            except Exception as e:
                st.error(f"❌ 執行失敗：{str(e)}")