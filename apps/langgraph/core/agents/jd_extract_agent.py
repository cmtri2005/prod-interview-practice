import json
from langchain_core.prompts import ChatPromptTemplate
from apps.langgraph.utils.state import AgentState
from apps.langgraph.core.agents.base_agent import BaseAgent
from apps.langgraph.schema.jd import JD
from apps.helper.logger import LoggerSingleton
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.messages import BaseMessage
from typing import Sequence, Annotated
from langchain_core.prompts import ChatPromptTemplate
from langgraph.utils.state import AgentState
from langgraph.core.agents.base_agent import BaseAgent
from langgraph.schema.jd import JD
from langgraph.utils.tools import docx_loader, pdf_loader


class JDExtractAgent(BaseAgent):
    def __init__(self, agent_name, llm, tools):
        super().__init__(agent_name, llm, tools)
        self.llm = llm
        self.logger = LoggerSingleton().get_instance()
        self.parser = JsonOutputParser()
        feild_des = "\n".join(
            f"- {name}: {field.description}" for name, field in JD.model_fields.items()
        )
        self.prompt = ChatPromptTemplate(
            [
                (
                    "system",
                    f"""You are a specialized Job Description (JD) extraction assistant.
                Extract the following fields and ONLY return valid JSON matching the schema:
                {feild_des}
                Return just the JSON object (no explanation).
                """,
                ),
                (
                    "human",
                    "Analyze JD: \n```{jd_content}```\n\n"
                    "{format_instructions}\nGenerate JD JSON",
                ),
            ]
        )

    def extract_jd(self, state: AgentState) -> AgentState:
        try:
            self.logger.info(f"[{self.agent_name}] is running...\n")
            messages: list = state.get("messages", [])
            # jd_file = state.get("jd_file")
            # jd_content = ""

            # try:
            #     self.logger.info(f"Loading JD from: {jd_file.filename}")
            #     jd_content = self.tools["file_loader"](jd_file)
            #     print(jd_content)
            # except Exception as e:
            #     self.logger.error(f"Error: {e}")
            #     raise ValueError(f"Failed to load JD file: {e}")
            jd_content = state.get("jd_text", "")

            chain = self.prompt | self.llm
            raw = chain.invoke(
                {
                    "jd_content": jd_content,
                    "format_instructions": self.parser.get_format_instructions(),
                }
            )
            text = (
                getattr(raw, "content", None) or getattr(raw, "text", None) or str(raw)
            )
            text = text.strip()
            jd_dict = self.parser.parse(text)
            messages.append(("ai", f"Job Description: {jd_dict}"))

            self.tools["save_raw_output"](
                "JD_output.json", json.dumps(jd_dict, indent=2, ensure_ascii=False)
            )

            self.logger.info(f"[{self.agent_name}] completed successfully.\n")
            return {"jd": JD(**jd_dict), "messages": messages}
        except Exception as e:
            self.logger.error(f"[{self.agent_name}] failed: {str(e)}", exc_info=True)
            raise ValueError(f"JD extraction failed: {str(e)}")

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

        chain = self.prompt | self.llm_with_structured_output(JD)
        jd = chain.invoke({"jd_content": jd_content})

        return {"jd": jd}
