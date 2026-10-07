import os
from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task

# 僅從環境變數讀取 API Key，絕不硬編碼明文 Key
api_key = os.getenv("OPENROUTER_API_KEY")

openrouter_llm = LLM(
    model="openrouter/deepseek/deepseek-chat",
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key
)

@CrewBase
class InternationalTradeLegalDocumentAutomation():
    """InternationalTradeLegalDocumentAutomation crew"""

    @agent
    def legal_researcher(self) -> Agent:
        return Agent(
            role="國際貿易法規研究員",
            goal="針對主題 {topic} 進行法規與合約條款分析",
            backstory="你是一位精通國際貿易法與跨國合約規範的法務專家。",
            llm=openrouter_llm,
            verbose=True
        )

    @agent
    def document_writer(self) -> Agent:
        return Agent(
            role="法律文件撰寫員",
            goal="根據研究結果，撰寫專業且嚴謹的國際貿易法律文件",
            backstory="你是一位經驗豐富的商務律師，擅長起草各類國際貿易合約與條款。",
            llm=openrouter_llm,
            verbose=True
        )

    @task
    def research_task(self) -> Task:
        return Task(
            description="針對 {topic} 分析相關法律風險與必要的合約條款。",
            expected_output="一份包含關鍵法規風險與注意事項的重點報告。",
            agent=self.legal_researcher()
        )

    @task
    def write_document_task(self) -> Task:
        return Task(
            description="根據分析報告，撰寫完整且規範的法律文件草案。",
            expected_output="一份格式完整的法律文件草案。",
            agent=self.document_writer()
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )