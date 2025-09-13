from langchain_core.prompts import ChatPromptTemplate
from apps.helper.logger import LoggerSingleton

from apps.langgraph.core.agents.base_agent import BaseAgent
from apps.langgraph.schema.learning_progress import Topic, LearningProgress
from apps.langgraph.utils.state import AgentState
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.messages import HumanMessage


class AnaLysisAgent(BaseAgent):
    def __init__(self, agent_name, llm, tools):
        super().__init__(agent_name, llm, tools)
        self.llm = llm
        self.logger = LoggerSingleton().get_instance()
        self.parser = JsonOutputParser()
        feild_des = "\n".join(f"- {name}: {field.description}" for name, field in Topic.model_fields.items())
        self.prompt = ChatPromptTemplate([
            ("system", f"""You are an instructional designer. 
                Given a Module json, generate a JSON array of topics that together allow a learner to achieve the aims. 
                Extract the following fields and ONLY return valid JSON matching the schema:
                {feild_des}
                Important:
                - Quiz must be []. It will be filled by another agent.
                Rules:
                - Topics should be distinct (no duplicates or near-duplicates) and at least 5 topics. But not more than 10 topic.
                - Each topic's description should clearly relate to the module's aims.
                - References should be relevant and credible resources that support the topic. If the topic is highly academic, reference scientific articles from prestigious conferences.
                - At least 2 references per topic.
                - Each aim should be addressed by at least one topic (best-effort).
                - Return strictly a JSON array of topic objects (no extra text). If you cannot produce topics, return [].
                """
            ),
            ("human", "PModule JSON:\n```{module_json}```\n\n""{format_instructions}\nGenerate array Topic JSON"),
        ])


    def run(self, state: AgentState) -> AgentState:
        try:
            self.logger.info(f"[{self.agent_name}] is running...")
            messages = state.get("messages", [])
            learningProgress: LearningProgress = state.get("learningProgress")
            
            idx_module = state.get("idx_module", None)
            if idx_module is None:
                messages.append(("human", "Please input idx_module"))
                return {
                    "learningProgress" : learningProgress,
                    "messages": messages,
                    "awaiting_input": True
                }

            try:
                idx = state.get("idx_module")
                module = learningProgress.modules[idx]
            except Exception as e:
                self.logger.error(f"Invalid selection: {state.get('idx_module')}")
                raise ValueError(f"Invalid selection: {state.get('idx_module')}") from e

            prompt_inputs = {
                "module_json": module.model_dump_json(),
                "format_instructions": self.parser.get_format_instructions()
            }
            chain = self.prompt | self.llm
            raw = chain.invoke(prompt_inputs)
            text = getattr(raw, "content", None) or getattr(raw, "text", None) or str(raw)
            text = text.strip()

            topic_array = self.parser.parse(text)
            module.topics = [Topic(**topic) for topic in topic_array]
            
            messages.append(("human", f"Index selected module: {idx}"))
            messages.append(("ai", f"Topics generated: {topic_array}"))

            self.tools["save_raw_output"](f"Module_selected{idx}_output.json", module.model_dump_json(indent=2))

            self.logger.info(f"[{self.agent_name}] completed successfully.")
            return {
                "learningProgress": learningProgress,
                "messages": messages,
                "awaiting_input": False,
                "idx_module": idx
            }

        except Exception as e:
            self.logger.error(f"[{self.agent_name}] failed: {e}")
            raise ValueError(f"[{self.agent_name}] failed: {e}")