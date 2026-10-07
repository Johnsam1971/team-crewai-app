import os
import sys
import streamlit as st

# 將 src 目錄納入 Python 模組搜尋路徑
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from international_trade_legal_document_automation.crews.crew import InternationalTradeLegalDocumentAutomation

# 頁面配置
st.set_page_config(
    page_title="國際貿易法律文件自動化系統",
    page_icon="⚖️",
    layout="wide"
)

st.title("⚖️ 國際貿易法律文件自動化系統")
st.markdown("填寫以下交易與合約資訊，AI 代理人團隊將為您自動生成**中英文對照版**專業法律文件。")

# 獲取 API Key
openrouter_key = st.secrets.get("OPENROUTER_API_KEY") or os.getenv("OPENROUTER_API_KEY")

if not openrouter_key:
    st.warning("⚠️ 未檢測到 OPENROUTER_API_KEY，請於側邊欄輸入：")
    openrouter_key = st.sidebar.text_input("輸入 OpenRouter API Key：", type="password")

if openrouter_key:
    os.environ["OPENROUTER_API_KEY"] = openrouter_key
    os.environ["OPENAI_API_KEY"] = openrouter_key
    os.environ["OPENAI_API_BASE"] = "https://openrouter.ai/api/v1"
    os.environ["OPENAI_BASE_URL"] = "https://openrouter.ai/api/v1"

# 表單分區輸入
st.subheader("📋 交易與合約資料填寫")

tab1, tab2, tab3, tab4 = st.tabs(["基本資訊", "出口/進口商資料", "產品細節", "貿易與付款條款"])

with tab1:
    document_type = st.selectbox(
        "文件類型 (document_type)*",
        ["Sales Contract (銷售合約)", "Purchase Agreement (採購協議)", "Agency Agreement (代理合約)", "NDA (保密協定)", "Other (其他)"]
    )
    target_import_country = st.text_input("目標進口國家 (target_import_country)", "United States")
    hs_code = st.text_input("HS Code 海關編號", "59111000")
    output_language = st.selectbox("文件輸出語言", ["中英文雙語對照版 (Bilingual CN/EN)", "僅英文 (English Only)", "僅中文 (Traditional Chinese Only)"])

with tab2:
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**出口商 (Exporter)**")
        exporter_name = st.text_input("出口商公司名稱", "ABC Technology Limited")
        exporter_address = st.text_input("出口商地址", "Room 101, B2 Building, Cyberport, Hong Kong")
        exporter_contact = st.text_input("出口商聯絡人/職稱", "John Sales / Sales Manager")
    with col2:
        st.markdown("**進口商 (Importer)**")
        importer_name = st.text_input("進口商公司名稱", "XYZ Global LLC")
        importer_address = st.text_input("進口商地址", "123 Market Street, San Francisco, CA, USA")
        importer_contact = st.text_input("進口商聯絡人/職稱", "Robert Director / Director")

with tab3:
    col3, col4 = st.columns(2)
    with col3:
        product_name = st.text_input("產品名稱與型號", "GeoTextile VIP1230")
        quantity = st.text_input("數量與單位", "100,000 SQM")
        unit_price = st.text_input("單價", "USD 2.50")
        currency = st.selectbox("交易幣別", ["USD", "EUR", "HKD", "CNY", "GBP"])
    with col4:
        total_price = st.text_input("總合約金額", "USD 250,000.00")
        packaging = st.text_input("包裝說明", "10 Rolls per carton, export standard carton")
        specifications = st.text_area("技術規格與描述", "200 Meter 170 g/m2 nonwoven geotextile Jumbo Roll", height=68)

with tab4:
    col5, col6 = st.columns(2)
    with col5:
        incoterm = st.text_input("國貿條規 (Incoterms)", "FOB Shenzhen Incoterms 2020")
        payment_method = st.text_input("付款方式", "T/T 30% deposit, 70% before shipment")
    with col6:
        inspection = st.text_input("檢驗要求", "No third-party inspection required")
        governing_law = st.text_input("管轄法律/仲裁地", "Laws of Hong Kong")

st.markdown("---")

# 提交按鈕與觸發 CrewAI
if st.button("🚀 開始生成雙語法律文件", type="primary", use_container_width=True):
    if not openrouter_key:
        st.error("請先提供 OpenRouter API Key！")
    else:
        with st.spinner("AI 代理人團隊正在根據輸入資料分析法規並起草中英文雙語文件，請稍候..."):
            try:
                # 組合傳給 CrewAI 的完整 Inputs 字典
                inputs = {
                    "document_type": document_type,
                    "target_import_country": target_import_country,
                    "hs_code": hs_code,
                    "language_requirement": output_language,
                    "topic": f"{document_type} for {product_name} ({output_language})",
                    "exporter_name": exporter_name,
                    "exporter_address": exporter_address,
                    "exporter_contact": exporter_contact,
                    "importer_name": importer_name,
                    "importer_address": importer_address,
                    "importer_contact": importer_contact,
                    "product_name": product_name,
                    "quantity": quantity,
                    "unit_price": unit_price,
                    "currency": currency,
                    "total_price": total_price,
                    "packaging": packaging,
                    "specifications": specifications,
                    "incoterm": incoterm,
                    "payment_method": payment_method,
                    "inspection": inspection,
                    "governing_law": governing_law
                }

                # 實例化並執行 Crew
                crew_instance = InternationalTradeLegalDocumentAutomation()
                result = crew_instance.crew().kickoff(inputs=inputs)
                result_text = str(result)

                st.success("✨ 中英文雙語文件生成成功！")
                st.markdown("### 📄 生成結果預覽")
                st.markdown(result_text)

                # 下載按鈕
                st.download_button(
                    label="📥 下載為 Markdown 雙語文件 (.md)",
                    data=result_text,
                    file_name=f"{document_type}_雙語合約草案.md",
                    mime="text/markdown"
                )
            except Exception as e:
                st.error(f"❌ 執行失敗：{str(e)}")