import os
import sys
import streamlit as st

# 將 src 目錄納入 Python 模組搜尋路徑
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from international_trade_legal_document_automation.crews.crew import InternationalTradeLegalDocumentAutomation

# 頁面標題配置
st.set_page_config(
    page_title="國際貿易法律文件自動化系統",
    page_icon="⚖️",
    layout="wide"
)

st.title("⚖️ 國際貿易法律文件自動化系統")
st.markdown("透過 AI Agent 自動進行跨國法規分析並起草專業法律合約。")

# 獲取 API Key（優先從 Streamlit Cloud Secrets 或環境變數讀取）
openrouter_key = st.secrets.get("OPENROUTER_API_KEY") or os.getenv("OPENROUTER_API_KEY")

# 側邊欄 API Key 輸入（備用選項）
if not openrouter_key:
    st.warning("⚠️ 未檢測到 OPENROUTER_API_KEY，請於側邊欄輸入或至 Streamlit Secrets 設定。")
    openrouter_key = st.sidebar.text_input("輸入 OpenRouter API Key：", type="password")

if openrouter_key:
    os.environ["OPENROUTER_API_KEY"] = openrouter_key
    os.environ["OPENAI_API_KEY"] = openrouter_key
    os.environ["OPENAI_API_BASE"] = "https://openrouter.ai/api/v1"
    os.environ["OPENAI_BASE_URL"] = "https://openrouter.ai/api/v1"

# 介面互動區
st.subheader("📝 輸入文件需求")
topic = st.text_input("請輸入法律文件主題或合約需求：", value="國際採購合約風險分析")

if st.button("🚀 開始生成文件", type="primary"):
    if not openrouter_key:
        st.error("請先提供 OpenRouter API Key！")
    elif not topic.strip():
        st.warning("請輸入有效的合約主題！")
    else:
        with st.spinner("AI 代理人團隊正在分析法規與起草文件中，請稍候..."):
            try:
                # 實例化純程式碼定義的 Crew
                crew_instance = InternationalTradeLegalDocumentAutomation()
                result = crew_instance.crew().kickoff(inputs={"topic": topic})
                result_text = str(result)

                st.success("✨ 文件生成成功！")
                st.markdown("---")
                st.markdown(result_text)

                # 下載按鈕
                st.download_button(
                    label="📥 下載為 Markdown 檔案 (.md)",
                    data=result_text,
                    file_name=f"{topic}_法律文件草案.md",
                    mime="text/markdown"
                )
            except Exception as e:
                st.error(f"❌ 執行失敗：{str(e)}")