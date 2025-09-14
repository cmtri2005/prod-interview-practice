from typing import Callable, Dict
import json
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.language_models.chat_models import BaseChatModel
from pydantic import ValidationError
from apps.langgraph.core.agents.base_agent import BaseAgent
from apps.langgraph.schema.learning_progress import LearningProgress
from apps.langgraph.schema.jd import JD
from apps.langgraph.utils.state import AgentState
from apps.helper.logger import LoggerSingleton
from langchain_core.output_parsers import JsonOutputParser
from apps.langgraph.schema.learning_progress import Module

class LearningProgressAgent(BaseAgent):
    def __init__(self, agent_name: str, llm: BaseChatModel, tools: Dict[str, Callable]):
        super().__init__(agent_name, llm, tools)
        self.llm = llm
        self.logger = LoggerSingleton().get_instance()
        self.parser = JsonOutputParser()
        field_des_learning_progress = "\n".join(f"- {name}: {field.description}" for name, field in LearningProgress.model_fields.items())
        field_des_module = "\n".join(f"- {name}: {field.description}" for name, field in Module.model_fields.items())
        self.prompt = ChatPromptTemplate([
            ("system", f"""You design actionable learning Progress from a JD JSON.
                Extract the following fields and ONLY return valid JSON matching the schema:
                {field_des_learning_progress}
                Each Module include schema: 
                {field_des_module}
                
                Important:
                - Return only the JSON object (no extra commentary).
                - At least 5 modules, but not more than 10 in Learning Progress.
                - Topics in module must return []. It will be filled by another agent.
                - Each module should have at least 3 aims.
                - Each aim should be achievable by the end of the module.
                - If you cannot produce the full JSON structure, return an empty JSON object so the caller can fallback.
                """
            ),
            ("human", "JD JSON:\n```{learningProgress_json}```\n\n"
             "{format_instructions}\nGenerate LearningProgress JSON"
        )])


    
    
    def run(self, state: AgentState) -> AgentState:
        
        self.logger.info(f"[{self.agent_name}] is running...\n")
        jd: JD = state.get("jd")
        messages = state.get("messages", [])
        
        ## MAIN         
        try:
            prompt_inputs = {
                "learningProgress_json": jd.model_dump_json(),
                "format_instructions": self.parser.get_format_instructions()
            }

            learningProgress_dict = self.invoke_chain(prompt_inputs, messages, MAX_RETRIES=3)

            self.tools["save_raw_output"]("LearningProgress_output.json", json.dumps(learningProgress_dict, indent=2, ensure_ascii=False))

            learningProgress = LearningProgress(**learningProgress_dict)
            messages.append(("ai", f"Learning Progress: {learningProgress}"))

            self.logger.info(f"[{self.agent_name}] completed successfully.\n")
            return {
                "learningProgress": learningProgress,
                "messages": messages,
                "next_agent": "Analyze_Modules_Agent"
            }
        
        except Exception as e:
            self.logger.error(f"[{self.agent_name}] failed: {str(e)}", exc_info=True)
            raise  ValueError(f"[{self.agent_name}] failed: {str(e)}")


    def invoke_chain(self, prompt_inputs: dict, messages: list, MAX_RETRIES: int) -> dict:
        
        chain = self.prompt | self.llm 
        raw = chain.invoke(prompt_inputs)
        text = getattr(raw, "content", None) or getattr(raw, "text", None) or str(raw)
        text = text.strip()
        parsed_dict = {}
        
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                parsed_dict = self.parser.parse(text)
                
                if (parsed_dict.get("modules") is None) or (len(parsed_dict.get("modules", [])) == 0):
                    self.logger.error("Modules is empty")
                    raise ValueError("Modules is empty")
                    
                break
            except (ValidationError, ValueError) as e:
                if attempt < MAX_RETRIES:
                    self.logger.debug(f"Validation failed, retrying {attempt}/{MAX_RETRIES}...")
                    raw = chain.invoke(prompt_inputs)
                    text = getattr(raw, "content", None) or getattr(raw, "text", None) or str(raw)
                    text = text.strip()
                else:
                    messages.append(("ai", f"Failed to parse Learning Progress after {MAX_RETRIES} attempts. Error: {e}"))
                    break

        return parsed_dict

    
    
