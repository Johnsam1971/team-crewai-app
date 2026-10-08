import os
import sys
import io
import re
from pathlib import Path
import markdown
import streamlit as st
from docx import Document
from docx.shared import Pt
from xhtml2pdf import pisa

# -----------------------------------------------------------------------------
# 動態添加路徑：解決深層目錄 crew.py 模組導入問題
# -----------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
CREWS_DIR = BASE_DIR / "src" / "international_trade_legal_document_automation" / "crews"
SRC_DIR = BASE_DIR / "src"

if str(CREWS_DIR) not in sys.path:
    sys.path.insert(0, str(CREWS_DIR))
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

# 嘗試導入 crew 模組
try:
    from crew import run_flow
except ImportError:
    from international_trade_legal_document_automation.crews.crew import run_flow

# 金鑰注入
if "OPENROUTER_API_KEY" in st.secrets:
    os.environ["OPENROUTER_API_KEY"] = st.secrets["OPENROUTER_API_KEY"]

st.set_page_config(page_title="國際貿易法律文件 AI 自動化系統", page_icon="⚖️", layout="wide")

# -----------------------------------------------------------------------------
# 高級 Markdown 轉 Word / PDF 工具函數（支援表格與邊框排版）
# -----------------------------------------------------------------------------
def md_to_docx(md_text: str) -> bytes:
    """將 Markdown 文字轉換為結構完整、支援表格與格式的 Word (.docx) 檔"""
    doc = Document()
    style = doc.styles['Normal']
    style.font.name = 'Arial'
    style.font.size = Pt(10)

    lines = md_text.split('\n')
    in_table = False
    table_data = []

    def flush_table(data):
        if not data:
            return
        clean_rows = []
        for r in data:
            cells = [c.strip() for c in r.split('|')[1:-1]]
            if cells and not all(re.match(r'^-+$', c.replace(':', '')) for c in cells if c):
                clean_rows.append(cells)
        
        if not clean_rows:
            return

        cols_count = max(len(r) for r in clean_rows)
        t = doc.add_table(rows=len(clean_rows), cols=cols_count)
        t.style = 'Table Grid'
        for r_idx, row in enumerate(clean_rows):
            for c_idx, val in enumerate(row):
                if c_idx < cols_count:
                    cell = t.cell(r_idx, c_idx)
                    cell.text = val
                    if r_idx == 0:
                        for p in cell.paragraphs:
                            for run in p.runs:
                                run.bold = True

    for line in lines:
        line_str = line.strip()
        
        if line_str.startswith('|') and line_str.endswith('|'):
            in_table = True
            table_data.append(line_str)
            continue
        else:
            if in_table:
                flush_table(table_data)
                table_data = []
                in_table = False

        if not line_str:
            doc.add_paragraph('')
            continue

        if line_str.startswith('# '):
            doc.add_heading(line_str[2:], level=1)
        elif line_str.startswith('## '):
            doc.add_heading(line_str[3:], level=2)
        elif line_str.startswith('### '):
            doc.add_heading(line_str[4:], level=3)
        elif line_str in ['---', '***']:
            p = doc.add_paragraph()
            p.add_run('─' * 50)
        elif line_str.startswith('- ') or line_str.startswith('* '):
            p = doc.add_paragraph(style='List Bullet')
            _add_formatted_text(p, line_str[2:])
        elif re.match(r'^\d+\. ', line_str):
            p = doc.add_paragraph(style='List Number')
            _add_formatted_text(p, re.sub(r'^\d+\. ', '', line_str))
        else:
            p = doc.add_paragraph()
            _add_formatted_text(p, line_str)

    if in_table:
        flush_table(table_data)

    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf.getvalue()

def _add_formatted_text(paragraph, text):
    parts = re.split(r'(\*\*[^*]+\*\*)', text)
    for part in parts:
        if part.startswith('**') and part.endswith('**'):
            run = paragraph.add_run(part[2:-2])
            run.bold = True
        else:
            paragraph.add_run(part)

def md_to_pdf(md_text: str) -> bytes:
    """將 Markdown 文字轉為 PDF (.pdf) 檔"""
    html_content = markdown.markdown(md_text, extensions=['tables', 'fenced_code'])
    styled_html = f"""
    <html>
    <head>
    <meta charset="utf-8">
    <style>
        body {{ font-family: Helvetica, Arial, sans-serif; font-size: 10pt; line-height: 1.4; margin: 20px; }}
        h1 {{ color: #1a365d; font-size: 16pt; border-bottom: 1px solid #ccc; }}
        h2 {{ color: #2b6cb0; font-size: 13pt; margin-top: 15px; }}
        h3 {{ color: #2d3748; font-size: 11pt; }}
        table {{ border-collapse: collapse; width: 100%; margin: 10px 0; }}
        th, td {{ border: 1px solid #dddddd; text-align: left; padding: 6px; font-size: 9pt; }}
        th {{ background-color: #f2f2f2; }}
    </style>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """
    buf = io.BytesIO()
    pisa.CreatePDF(styled_html, dest=buf)
    buf.seek(0)
    return buf.getvalue()

def show_download_buttons(md_text: str, filename_prefix: str = "trade_document"):
    col1, col2, col3 = st.columns(3)
    with col1:
        st.download_button("⬇️ 下載 Markdown (.md)", data=md_text.encode('utf-8'), file_name=f"{filename_prefix}.md", mime="text/markdown")
    with col2:
        docx_bytes = md_to_docx(md_text)
        st.download_button("⬇️ 下載 Word (.docx)", data=docx_bytes, file_name=f"{filename_prefix}.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    with col3:
        pdf_bytes = md_to_pdf(md_text)
        st.download_button("⬇️ 下載 PDF (.pdf)", data=pdf_bytes, file_name=f"{filename_prefix}.pdf", mime="application/pdf")

# -----------------------------------------------------------------------------
# Streamlit 表單 UI 介面
# -----------------------------------------------------------------------------
st.title("⚖️ 國際貿易法律文件 AI 自動生成系統")
st.markdown("填寫下方交易資訊，系統將自動調用 CrewAI + DeepSeek 生成完全無佔位符的正式文件。")

with st.form("trade_form"):
    st.header("1. 基本合約資訊與文件類型")
    c1, c2, c3, c4 = st.columns(4)
    document_type = c1.selectbox("文件類型", ["Sales Contract (銷售合約)", "Proforma Invoice (形式發票)", "Commercial Invoice (商業發票)"])
    contract_no = c2.text_input("合約編號", "GeoTextile-VIP1230-2026")
    contract_date = c3.text_input("簽署日期", "2026-10-08")
    effective_date = c4.text_input("生效日期", "2026-10-08")

    c5, c6 = st.columns(2)
    target_import_country = c5.text_input("目標進口國", "United States")
    hs_code = c6.text_input("HS Code", "5603.93.00")

    st.header("2. 出口商 (Exporter / Seller) 資料")
    e1, e2 = st.columns(2)
    exporter_company_name = e1.text_input("出口商公司名稱", "Plantech Industries PTE Ltd")
    exporter_address = e2.text_input("出口商地址", "10 Anson Road #26-04, International Plaza, Singapore")
    e3, e4 = st.columns(2)
    exporter_reg_no = e3.text_input("出口商註冊號", "201812345M")
    exporter_tax_id = e4.text_input("出口商稅號", "GST-987654321")
    e5, e6, e7 = st.columns(3)
    exporter_contact_title = e5.text_input("出口商聯絡人職稱", "Sales Director")
    exporter_contact_name = e6.text_input("出口商聯絡人姓名", "John Doe")
    exporter_phone = e7.text_input("出口商電話", "+65 6123 4567")
    e8, e9, e10 = st.columns(3)
    exporter_email = e8.text_input("出口商 Email", "export@plantech.com")
    exporter_auth_rep = e9.text_input("出口授權代表姓名", "Johnson")
    exporter_auth_rep_title = e10.text_input("出口授權代表職稱", "CEO")

    st.header("3. 進口商 (Importer / Buyer) 資料")
    i1, i2 = st.columns(2)
    importer_company_name = i1.text_input("進口商公司名稱", "Plantech Dynamic Technology (Vietnam) Limited")
    importer_address = i2.text_input("進口商地址", "No. 15, VSIP Bac Ninh, Tu Son, Bac Ninh Province, Vietnam")
    i3, i4 = st.columns(2)
    importer_reg_no = i3.text_input("進口商註冊號", "0109876543")
    importer_tax_id = i4.text_input("進口商稅號", "VN-11223344")
    i5, i6, i7 = st.columns(3)
    importer_contact_title = i5.text_input("進口商聯絡人職稱", "Procurement Manager")
    importer_contact_name = i6.text_input("進口商聯絡人姓名", "Nguyen Van A")
    importer_phone = i7.text_input("進口商電話", "+84 222 3888 999")
    i8, i9, i10 = st.columns(3)
    importer_email = i8.text_input("進口商 Email", "import@plantech.vn")
    importer_auth_rep = i9.text_input("進口授權代表姓名", "Robert")
    importer_auth_rep_title = i10.text_input("進口授權代表職稱", "Director")

    st.header("4. 商品細節")
    p1, p2, p3 = st.columns(3)
    product_name = p1.text_input("商品名稱", "GeoTextile VIP1230")
    product_qty = p2.number_input("數量 (Rolls)", value=100000)
    currency = p3.selectbox("幣別", ["USD", "EUR", "HKD", "SGD"])
    p4, p5 = st.columns(2)
    unit_price = p4.number_input("單價", value=2.50)
    total_price = p5.number_input("總價", value=250000.0)
    product_description = st.text_area("商品描述", "200-meter, 70 g/m², black, nonwoven geotextile jumbo rolls, packed ten (10) rolls per carton.")
    product_specs = st.text_input("產品規格", "Width: 2m; Length: 200m; Density: 70g/m²; Color: Black")
    product_packaging = st.text_input("包裝方式", "10 rolls per export-standard carton, 10,000 cartons total")

    st.header("5. 運輸與支付條件")
    t1, t2, t3 = st.columns(3)
    place_of_production = t1.text_input("生產地/裝運港", "Hai Phong Port, Vietnam")
    port_of_discharge = t2.text_input("卸貨港/目的港", "Port of Los Angeles, USA")
    incoterm = t3.selectbox("Incoterms 條款", ["FOB", "CIF", "EXW", "DDP"])
    t4, t5 = st.columns(2)
    production_date = t4.date_input("預計生產日")
    delivery_date = t5.date_input("預計裝運/交貨日")
    m1, m2 = st.columns(2)
    payment_method = m1.selectbox("付款方式", ["T/T (Telegraphic Transfer)", "L/C (Letter of Credit)", "D/P"])
    payment_timing = m2.text_input("付款時機", "30% Deposit upon signing, 70% T/T before shipment")
    bank_details = st.text_input("銀行帳戶資料", "DBS Bank Singapore, A/C: 123-456789-0, SWIFT: DBSSSGSG")
    w1, w2, w3 = st.columns(3)
    warranty_period = w1.text_input("保固期", "12 months from delivery date")
    governing_law = w2.text_input("準據法", "Laws of Hong Kong")
    dispute_resolution = w3.text_input("爭議解決機制", "Hong Kong International Arbitration Centre (HKIAC)")
    partial_shipment = st.selectbox("是否允許分批裝運/轉運", ["Allowed", "Not Allowed"])

    submitted = st.form_submit_button("🚀 開始生成法律文件", type="primary")

# -----------------------------------------------------------------------------
# 執行 CrewAI 生成與展示
# -----------------------------------------------------------------------------
if submitted:
    inputs = {
        "document_type": document_type,
        "contract_no": contract_no,
        "contract_date": str(contract_date),
        "effective_date": str(effective_date),
        "target_import_country": target_import_country,
        "hs_code": hs_code,
        "place_of_production": place_of_production,
        "port_of_discharge": port_of_discharge,
        "exporter_company_name": exporter_company_name,
        "exporter_address": exporter_address,
        "exporter_reg_no": exporter_reg_no,
        "exporter_tax_id": exporter_tax_id,
        "exporter_contact_title": exporter_contact_title,
        "exporter_contact_name": exporter_contact_name,
        "exporter_phone": exporter_phone,
        "exporter_email": exporter_email,
        "exporter_auth_rep": exporter_auth_rep,
        "exporter_auth_rep_title": exporter_auth_rep_title,
        "importer_company_name": importer_company_name,
        "importer_address": importer_address,
        "importer_reg_no": importer_reg_no,
        "importer_tax_id": importer_tax_id,
        "importer_contact_title": importer_contact_title,
        "importer_contact_name": importer_contact_name,
        "importer_phone": importer_phone,
        "importer_email": importer_email,
        "importer_auth_rep": importer_auth_rep,
        "importer_auth_rep_title": importer_auth_rep_title,
        "product_name": product_name,
        "product_description": product_description,
        "product_qty": str(product_qty),
        "unit_price": str(unit_price),
        "total_price": str(total_price),
        "currency": currency,
        "product_specs": product_specs,
        "product_packaging": product_packaging,
        "incoterm": incoterm,
        "payment_method": payment_method,
        "payment_timing": payment_timing,
        "bank_details": bank_details,
        "warranty_period": warranty_period,
        "governing_law": governing_law,
        "dispute_resolution": dispute_resolution,
        "partial_shipment": partial_shipment,
        "delivery_date": str(delivery_date),
        "production_date": str(production_date),
    }

    with st.spinner("DeepSeek AI 正在整合表單資料並編撰正式合約..."):
        try:
            result_text = run_flow(inputs)
            st.session_state.result = result_text
            st.success("文件生成成功！已自動將表單資料完全填入合約中。")
        except Exception as e:
            st.error(f"生成過程發生錯誤: {str(e)}")

if "result" in st.session_state and st.session_state.result:
    st.markdown("---")
    st.subheader("📄 生成文件預覽")
    st.markdown(st.session_state.result)

    st.markdown("---")
    st.subheader("📥 下載文件")
    show_download_buttons(
        md_text=st.session_state.result,
        filename_prefix=f"{contract_no}_Document"
    )