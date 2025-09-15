import json
from langchain_core.prompts import ChatPromptTemplate
from pydantic import ValidationError
from apps.langgraph.utils.state import AgentState
from apps.langgraph.core.agents.base_agent import BaseAgent
from apps.langgraph.schema.jd import JD
from apps.helper.logger import LoggerSingleton
from langchain_core.output_parsers import JsonOutputParser



class JDExtractAgent(BaseAgent):
    def __init__(self, agent_name, llm, tools):
        super().__init__(agent_name, llm, tools)
        self.llm = llm
        self.logger = LoggerSingleton().get_instance()
        self.MAX_RETRIES = 3 ## clean sau
        self.parser = JsonOutputParser()
        feild_des = "\n".join(
            f"- {name}: {field.description}" for name, field in JD.model_fields.items()
        )
        self.prompt = ChatPromptTemplate([(
            "system",
            f"""You are a specialized Job Description (JD) extraction assistant.
            Extract the following fields and ONLY return valid JSON matching the schema:
            {feild_des}
            Return just the JSON object (no explanation).
            """,),
            (
            "human",
            "Analyze JD: \n```{jd_content}```\n\n"
            "{format_instructions}\nGenerate JD JSON",
        )])

    def run(self, state: AgentState) -> AgentState:
        self.logger.info(f"[{self.agent_name}] is running...\n")
        messages: list = state.get("messages", [])
        jd_content = state.get("jd_text", "")
        
        try:
            prompt_inputs = {
                "jd_content": jd_content,
                "format_instructions": self.parser.get_format_instructions(),
            }

            jd : JD = self.invoke_chain(prompt_inputs, messages)

            self.tools["save_raw_output"](
                "JD_output.json", json.dumps(jd.model_dump_json(), indent=2, ensure_ascii=False)
            )

            messages.append(("ai", f"JD Extraction: {jd}"))

            self.logger.info(f"[{self.agent_name}] completed successfully.\n")
            return {
                "jd": jd,
                "messages": messages,
                "next_agent": "Learning_Progress_Agent" 
            }
        except Exception as e:
            self.logger.error(f"[{self.agent_name}] failed: {str(e)}", exc_info=True)
            raise ValueError(f"[{self.agent_name}] failed: {str(e)}")

        
    def invoke_chain(self, prompt_inputs: dict, messages: list) -> JD:
        chain = self.prompt | self.llm 
        raw = chain.invoke(prompt_inputs)
        text = getattr(raw, "content", None) or getattr(raw, "text", None) or str(raw)
        text = text.strip()
        parsed_dict = {}
        jd : JD = None

        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                parsed_dict = self.parser.parse(text)
                jd : JD = JD(**parsed_dict)
                return jd
            except (ValidationError, ValueError) as e:
                if attempt < self.MAX_RETRIES:
                    self.logger.debug(f"Validation failed, retrying {attempt}/{self.MAX_RETRIES}...")
                    raw = chain.invoke(prompt_inputs)
                    text = getattr(raw, "content", None) or getattr(raw, "text", None) or str(raw)
                    text = text.strip()
                else:
                    messages.append(("ai", f"Failed to parse JD Extraction after {self.MAX_RETRIES} attempts. Error: {e}"))
                    break

        return jd

