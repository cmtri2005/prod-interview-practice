from typing import Any, Callable, Dict
import json
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.output_parsers import JsonOutputParser
from apps.langgraph.core.agents.base_agent import BaseAgent
from apps.langgraph.schema.learning_progress import LearningProgress
from apps.langgraph.schema.jd import JD
from apps.langgraph.utils.state import AgentState
from apps.helper.logger import LoggerSingleton


class Rag(BaseAgent):
    def __init__(self, agent_name: str, llm: BaseChatModel, tools: Dict[str, Callable]):
        super().__init__(agent_name, llm, tools)
        self.llm = llm
        self.logger = LoggerSingleton().get_instance()
        self.parser = JsonOutputParser()
        
        with open("/mnt/d/Desktop/Desktop/MLOps/prod-interview-practice/details.json", "r", encoding="utf-8") as f:
            self.data = json.load(f)

        # Build list of IDs in readable form
        all_ids_str = "\n".join(
            f"{i} - {item['id']}" for i, item in enumerate(self.data) if "id" in item
        )

        # Prompt template for RAG
        self.prompt = ChatPromptTemplate.from_messages([(
                "system",
                f"""You are a helpful assistant that matches concepts to the most relevant knowledge pages.  
                Here is the list of all available knowledge IDs:
                {all_ids_str}
                Instructions:
                - Carefully read the provided concept JSON.
                - Identify the knowledge ID(s) from the list above that are most relevant.
                - Only return JSON in the following schema:
                    "matched_idx": ["1", "2"]
                Do not include explanations or extra text.
                """,),
            (
                "human",
                "Concept JSON:\n```{concept_json}```"
                "{format_instructions}\nGenerate index matched JSON",
            ),
        ])

    def Learning_Progress_rag(self, state: AgentState) -> AgentState:
        self.logger.info(f"[{self.agent_name}] is running...\n")
        jd: JD = state.get("jd")

        agentstate = {"next_agent": "Learning_Progress_Agent"}
        agentstate.update(self.invoke_rag(jd, state))
        return agentstate
    
    def Module_rag(self, state: AgentState) -> AgentState:
        self.logger.info(f"[{self.agent_name}] is running...\n")
        learningProgress: LearningProgress = state.get("learningProgress")
        idx_module = state.get("idx_module")
        module = learningProgress.modules[idx_module]
        messages = state.get("messages")

        agentstate = {
            "idx_module": idx_module,
            "messages": messages,
            "learningProgress": learningProgress,
            "next_agent": "Analyze_Modules_Agent"
        }
        agentstate.update(self.invoke_rag(module))
        return agentstate
    

    def invoke_rag(self, concept: Any):
        try:
            prompt_inputs = {
                "concept_json": concept.model_dump_json(),
                "format_instructions": self.parser.get_format_instructions()
            }

            # Ensure parsing with JsonOutputParser
            chain = self.prompt | self.llm | self.parser
            raw = chain.invoke(prompt_inputs)
            print("===============================")
            print(raw)
            list_id = raw["matched_idx"]
            knowledge = ""
            for i in list_id:
                knowledge += self.data[int(i)]["id"] + ": " + ", ".join(self.data[int(i)]["labels"]) + "\n"
            
            self.logger.info(f"[{self.agent_name}] completed successfully.\n")
            return {
                "knowledge_rag": knowledge
            }

        except Exception as e:
            self.logger.error(f"[{self.agent_name}] failed: {str(e)}", exc_info=True)
            raise ValueError(f"[{self.agent_name}] failed: {str(e)}")

# class match_id(BaseChatModel):
#     list_id: list[str] = Field(default_factory=list)