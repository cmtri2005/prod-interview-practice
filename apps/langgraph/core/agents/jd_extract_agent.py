from langchain_core.prompts import ChatPromptTemplate
from langgraph.utils.state import AgentState
from langgraph.agents.base_agent import BaseAgent
from langgraph.schema.jd import JD
from langgraph.utils.tools import docx_loader, pdf_loader


class JDExtractAgent(BaseAgent):
    def __init__(self, agent_name, llm, tools):
        super().__init__(agent_name, llm, tools)
        self.prompt = self.jd_extract_prompt()

    def jd_extract_prompt(self) -> ChatPromptTemplate:
        return ChatPromptTemplate(
            [
                (
                    "system",
                    """
                    You are a specialized Job Description (JD) extraction assistant.
                    Your task is to analyze the JD between triple backticks and extract structured information.
                    If the JD is not provided, reply "EMPTY"
                    """,
                ),
                ("human", "Please analyze the following JD: ```{jd_content}```"),
            ]
        )

    def extract_jd(self, state: AgentState) -> AgentState:
        jd_path = state["jd_path"]
        jd_content = ""

        try:
            if "pdf" in jd_path.split("."):
                self.logger.info(f"Extract content PDF file: {jd_path}")
                jd_content = pdf_loader(jd_path)
            elif "docx" in jd_path.split("."):
                self.logger.info(f"Extract content DOCX file: {jd_path}")
                jd_content = docx_loader(jd_path)
            else:
                jd_content = ""
                self.logger.warning(f"Undefined file: {jd_path}")

        except Exception as e:
            self.logger.error(f"Error: {e}")

        chain = self.prompt | self.llm.with_structured_output(JD)
        jd = chain.invoke({"jd_content": jd_content})

        return {"jd": jd}
