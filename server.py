import os
import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

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

try:
    from crew import run_flow
except ImportError:
    from international_trade_legal_document_automation.crews.crew import run_flow

openrouter_key = os.getenv("OPENROUTER_API_KEY")
if openrouter_key:
    os.environ["OPENAI_API_KEY"] = openrouter_key
    os.environ["OPENAI_API_BASE"] = "https://openrouter.ai/api/v1"

app = FastAPI(title="International Trade Document API", version="1.1")

class TradeDocumentRequest(BaseModel):
    document_type: str = "Sales Contract (銷售合約)"
    contract_no: Optional[str] = "GeoTextile-VIP1230-2026"
    contract_date: Optional[str] = "2026-10-08"
    effective_date: Optional[str] = "2026-10-08"
    target_import_country: str = "United States"
    hs_code: str = "5603.93.00"
    place_of_production: str = "Hai Phong Port, Vietnam"
    port_of_discharge: str = "Port of Los Angeles, USA"
    exporter_company_name: str = "Plantech Industries PTE Ltd"
    exporter_address: str = "10 Anson Road #26-04, International Plaza, Singapore"
    exporter_reg_no: str = "201812345M"
    exporter_tax_id: str = "GST-987654321"
    exporter_contact_title: str = "Sales Director"
    exporter_contact_name: str = "John Doe"
    exporter_phone: str = "+65 6123 4567"
    exporter_email: str = "export@plantech.com"
    exporter_auth_rep: str = "Johnson"
    exporter_auth_rep_title: str = "CEO"
    importer_company_name: str = "American Hospitality Properties REIT, Inc."
    importer_address: str = "14643 Dallas Parkway, Suite 970, Dallas, TX 75254, United States"
    importer_reg_no: str = "7010469"
    importer_tax_id: str = "83-2386947"
    importer_contact_title: str = "Procurement Manager"
    importer_contact_name: str = "Robert Lee"
    importer_phone: str = "+1-214-7502967"
    importer_email: str = "john.dave@phoenixamericanhospitality.com"
    importer_auth_rep: str = "Joe Reardon"
    importer_auth_rep_title: str = "Director"
    product_name: str = "GeoTextile VIP1230"
    product_description: str = "200-meter, 70 g/m², black, nonwoven geotextile jumbo rolls."
    product_qty: str = "100000"
    unit_price: str = "2.50"
    total_price: str = "250000.0"
    currency: str = "USD"
    product_specs: str = "Width: 2m; Length: 200m; Density: 70g/m²"
    product_packaging: str = "10 rolls per export carton"
    incoterm: str = "FOB"
    payment_method: str = "T/T"
    payment_timing: str = "30% Deposit, 70% before shipment"
    bank_details: str = "DBS Bank Singapore, A/C: 123-456789-0"
    warranty_period: str = "12 months"
    governing_law: str = "Laws of Hong Kong"
    dispute_resolution: str = "HKIAC Arbitration"
    partial_shipment: str = "Allowed"
    delivery_date: str = "2026-12-01"
    production_date: str = "2026-11-01"

@app.post("/generate-document")
def generate_document(payload: TradeDocumentRequest):
    try:
        inputs = payload.dict()
        result = run_flow(inputs)
        return {"status": "success", "document": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)