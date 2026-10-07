import os
import sys
import io
import streamlit as st

# 匯入文件轉換套件
from docx import Document
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

# 將 src 目錄納入 Python 模組搜尋路徑
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from international_trade_legal_document_automation.crews.crew import InternationalTradeLegalDocumentAutomation

# -----------------------------------------------------------------------------
# 輔助函式：將文字轉為 Word 檔案 (BytesIO)
# -----------------------------------------------------------------------------
def create_word_docx(text_content: str) -> io.BytesIO:
    doc = Document()
    doc.add_heading('國際貿易文件與風險評估報告', level=0)
    
    # 按行寫入 Word，保留 basic 排版
    for line in text_content.split('\n'):
        line_str = line.strip()
        if not line_str:
            continue
        if line_str.startswith('# '):
            doc.add_heading(line_str.replace('# ', ''), level=1)
        elif line_str.startswith('## '):
            doc.add_heading(line_str.replace('## ', ''), level=2)
        elif line_str.startswith('### '):
            doc.add_heading(line_str.replace('### ', ''), level=3)
        elif line_str.startswith('* ') or line_str.startswith('- '):
            doc.add_paragraph(line_str[2:], style='List Bullet')
        else:
            doc.add_paragraph(line_str)
            
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# -----------------------------------------------------------------------------
# 輔助函式：將文字轉為 PDF 檔案 (BytesIO)
# -----------------------------------------------------------------------------
def create_pdf(text_content: str) -> io.BytesIO:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # 建立自訂段落樣式
    body_style = ParagraphStyle('CustomBody', parent=styles['Normal'], spaceAfter=6, leading=14)
    heading_style = ParagraphStyle('CustomHeading', parent=styles['Heading2'], spaceAfter=10, leading=18)
    
    story = []
    for line in text_content.split('\n'):
        line_str = line.strip()
        if not line_str:
            story.append(Spacer(1, 6))
            continue
        
        # 轉義 HTML 敏感字元
        safe_text = line_str.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        
        if safe_text.startswith('#'):
            clean_text = safe_text.lstrip('#').strip()
            story.append(Paragraph(f"<b>{clean_text}</b>", heading_style))
        else:
            story.append(Paragraph(safe_text, body_style))
            
    doc.build(story)
    buffer.seek(0)
    return buffer

# -----------------------------------------------------------------------------
# Streamlit 頁面主體
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="國際貿易自動化文件與風險分析系統",
    page_icon="⚖️",
    layout="wide"
)

st.title("⚖️ 國際貿易自動化文件與風險分析系統")
st.markdown("填寫下方交易與合約資訊，AI Agent 團隊將為您自動生成**中英文專業貿易文件**及**風險評估建議報告**。")

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

st.subheader("📋 Run Parameters / 交易資料表單")

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
            ]
        )
        target_import_country = st.text_input("target_import_country *", "United States")
    with col2:
        hs_code = st.text_input("hs_code *", "5911.10")
        output_language = st.selectbox("文件語言版本", ["中英文雙語對照版 (Bilingual CN/EN)", "僅英文 (English Only)", "僅中文 (Traditional Chinese Only)"])

with tab2:
    st.markdown("#### Exporter Information")
    ex_col1, ex_col2 = st.columns(2)
    with ex_col1:
        exporter_company_name = st.text_input("company_name (Exporter)", "ABC Manufacturing Ltd.")
        exporter_address = st.text_area("address (Exporter)", "123 Industrial Road, Shenzhen, Guangdong, China 518000", height=68)
        exporter_tax_id = st.text_input("tax_id (Exporter)", "91440300MA5DXXXX00")
        exporter_company_reg = st.text_input("company_registration_no (Exporter)", "91440300MA5DXXXX00")
    with ex_col2:
        exporter_contact_title = st.text_input("contact_title (Exporter)", "Mr. John Smith")
        exporter_contact_email = st.text_input("contact_email (Exporter)", "john.smith@abcmfg.com")
        exporter_contact_phone = st.text_input("contact_phone (Exporter)", "+86-755-12345678")
        exporter_auth_rep = st.text_input("authorized_representative (Exporter)", "John Smith")
        exporter_auth_rep_title = st.text_input("authorized_rep_title (Exporter)", "General Manager")

with tab3:
    st.markdown("#### Importer Information")
    im_col1, im_col2 = st.columns(2)
    with im_col1:
        importer_company_name = st.text_input("company_name (Importer)", "XYZ Trading Inc.")
        importer_address = st.text_area("address (Importer)", "456 Commerce Street, Los Angeles, CA 90001, USA", height=68)
        importer_tax_id = st.text_input("tax_id (Importer)", "12-3456789")
        importer_company_reg = st.text_input("company_registration_no (Importer)", "US-EIN-12-3456789")
    with im_col2:
        importer_contact_title = st.text_input("contact_title (Importer)", "Mr. Robert Lee")
        importer_contact_email = st.text_input("contact_email (Importer)", "robert.lee@xyztrading.com")
        importer_contact_phone = st.text_input("contact_phone (Importer)", "+1-213-5559876")
        importer_auth_rep = st.text_input("authorized_representative (Importer)", "Robert Lee")
        importer_auth_rep_title = st.text_input("authorized_rep_title (Importer)", "President")

with tab4:
    st.markdown("#### Product Details")
    p_col1, p_col2 = st.columns(2)
    with p_col1:
        product_name = st.text_input("name *", "Wireless Bluetooth Headphones Model BT-500")
        currency = st.selectbox("currency *", ["USD", "EUR", "GBP", "JPY", "AUD", "CAD", "CNY", "HKD"])
        quantity = st.text_input("quantity *", "1000 UNITS")
        unit_price = st.text_input("unit_price *", "45.00")
        total_price = st.text_input("total_price *", "45000.00")
    with p_col2:
        packaging = st.text_input("packaging *", "10 PCS per carton, export standard carton 40x30x25cm, total 100 cartons")
        production_date = st.text_input("production_date *", "2026-11")
        description = st.text_area("description *", "Wireless stereo headphones with active noise cancellation, Bluetooth 5.0, rechargeable lithium battery", height=68)
        specifications = st.text_area("specifications *", "Material: ABS plastic + aluminum; Weight: 280g; Battery: 500mAh; Color: Black", height=68)

with tab5:
    st.markdown("#### Trade Terms & Logistics")
    t_col1, t_col2 = st.columns(2)
    with t_col1:
        incoterm = st.text_input("incoterm *", "FOB Shenzhen Incoterms 2020")
        payment_method = st.text_input("payment_method *", "T/T 30% deposit, 70% before shipment")
        payment_timing = st.text_input("payment_timing", "30% deposit within 7 days of contract signing, 70% balance before shipment")
        inspection = st.text_input("inspection *", "SGS pre-shipment inspection at seller expense")
        bank_details = st.text_input("bank_details", "Bank of China, Shenzhen Branch; A/C: 1234567890; SWIFT: BKCHCNBJ")
        governing_law = st.text_input("governing_law *", "Laws of Hong Kong")
        dispute_resolution = st.text_input("dispute_resolution", "Arbitration under HKIAC Rules, seat Hong Kong")
    with t_col2:
        place_of_production = st.text_input("place_of_production *", "CHINA")
        port_of_discharge = st.text_input("port_of_discharge *", "Los Angeles")
        warranty_period = st.text_input("warranty_period", "12 months from date of delivery")
        partial_shipment = st.text_input("partial_shipment", "Partial shipment allowed, transshipment not allowed")
        estimated_production_date = st.text_input("estimated_production_date", "2026-10-31")
        estimated_delivery_date = st.text_input("estimated_delivery_date", "2026-11-30")

st.markdown("---")

if st.button(f"🚀 開始生成【{document_type}】文件與風險評估報告", type="primary", use_container_width=True):
    if not openrouter_key:
        st.error("請先提供 OpenRouter API Key！")
    else:
        with st.spinner(f"AI Agent 團隊正在處理【{document_type}】資料並進行分析，請稍候..."):
            try:
                inputs = {
                    "document_type": document_type,
                    "target_import_country": target_import_country,
                    "hs_code": hs_code,
                    "language_requirement": output_language,
                    "place_of_production": place_of_production,
                    "port_of_discharge": port_of_discharge,
                    "topic": f"{document_type} for {product_name} ({output_language})",
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
                    }
                }

                crew_instance = InternationalTradeLegalDocumentAutomation()
                result = crew_instance.crew().kickoff(inputs=inputs)
                result_text = str(result)

                st.success(f"✨ 【{document_type}】文件與風險分析報告生成成功！")
                
                # 預覽區域
                st.markdown("### 📄 文件內容與風險建議報告預覽")
                st.markdown(result_text)

                st.markdown("---")
                st.markdown("### 📥 一鍵下載多格式文件")
                
                # 多列按鈕：下載 Markdown / Word (.docx) / PDF (.pdf)
                d_col1, d_col2, d_col3 = st.columns(3)
                
                # 1. 下載 Markdown
                with d_col1:
                    st.download_button(
                        label="📝 下載 Markdown (.md)",
                        data=result_text,
                        file_name=f"{document_type.replace(' ', '_')}_report.md",
                        mime="text/markdown",
                        use_container_width=True
                    )
                
                # 2. 下載 Word (.docx)
                with d_col2:
                    word_file = create_word_docx(result_text)
                    st.download_button(
                        label="📄 下載 Word 檔 (.docx)",
                        data=word_file,
                        file_name=f"{document_type.replace(' ', '_')}_report.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        use_container_width=True
                    )
                
                # 3. 下載 PDF (.pdf)
                with d_col3:
                    pdf_file = create_pdf(result_text)
                    st.download_button(
                        label="📕 下載 PDF 檔 (.pdf)",
                        data=pdf_file,
                        file_name=f"{document_type.replace(' ', '_')}_report.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )

            except Exception as e:
                st.error(f"❌ 執行失敗：{str(e)}")