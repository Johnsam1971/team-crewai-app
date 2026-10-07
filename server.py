import os

# 僅動態讀取環境變數，移除明文預設 Key
openrouter_key = os.getenv("OPENROUTER_API_KEY")
if openrouter_key:
    os.environ["OPENAI_API_KEY"] = openrouter_key
    os.environ["OPENAI_API_BASE"] = "https://openrouter.ai/api/v1"
    os.environ["OPENAI_BASE_URL"] = "https://openrouter.ai/api/v1"

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

from international_trade_legal_document_automation.crews.crew import InternationalTradeLegalDocumentAutomation

app = FastAPI(
    title="International Trade Legal Document Automation API",
    version="1.0.0"
)

class RunRequest(BaseModel):
    topic: str = Field(..., description="要分析或生成的法律文件主題", example="國際採購合約風險分析")
    extra_inputs: Optional[Dict[str, Any]] = Field(default=None, description="額外輸入參數")

@app.get("/")
async def root():
    return {"message": "API 服務運作正常，請存取 /docs 查看 Swagger UI 測試介面"}

@app.post("/api/v1/run")
async def run_crew(request: RunRequest):
    try:
        inputs = {"topic": request.topic}
        if request.extra_inputs:
            inputs.update(request.extra_inputs)

        crew_instance = InternationalTradeLegalDocumentAutomation()
        result = await crew_instance.crew().kickoff_async(inputs=inputs)
        
        return {
            "status": "success",
            "result": str(result)
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"CrewAI 執行失敗: {str(e)}"
        )