import os
from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task

@CrewBase
class InternationalTradeLegalDocumentAutomation():
    """InternationalTradeLegalDocumentAutomation crew"""

    def get_llm(self) -> LLM:
        """動態取得 LLM 配置，確保能在執行時成功讀取最新的 API Key"""
        api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
        return LLM(
            model="openrouter/deepseek/deepseek-chat",
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
            max_tokens=8192
        )

    @agent
    def legal_researcher(self) -> Agent:
        return Agent(
            role="國際貿易法規研究員",
            goal="針對主題 {topic} 進行法規與合約條款分析",
            backstory="你是一位精通國際貿易法與跨國合約規範的法務專家。",
            llm=self.get_llm(),
            verbose=True
        )

    @agent
    def document_writer(self) -> Agent:
        return Agent(
            role="法律文件撰寫員",
            goal="根據研究結果，撰寫專業且嚴謹的國際貿易法律文件",
            backstory="你是一位經驗豐富的商務律師，擅長起草各類國際貿易合約與條款。",
            llm=self.get_llm(),
            verbose=True
        )

    @task
    def write_document_task(self) -> Task:
        return Task(
            description="針對 {topic} 撰寫完整且規範的中英文雙語國際貿易銷售合約本文（包含 Clause 1 至 Clause 22）。",
            expected_output="完整且具體的雙語貿易合約條款全文。",
            agent=self.document_writer()
        )

    @task
    def research_task(self) -> Task:
        return Task(
            description="根據已撰寫好的合約條款與交易背景 {topic}，進行合約風險評估，並輸出風險建議報告（Clause 23 交易風險與補充注意事項）。",
            expected_output="一份針對前述合約條款的關鍵法規風險與注意事項報告。",
            agent=self.legal_researcher()
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )