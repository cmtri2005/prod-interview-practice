from langchain_core.prompts import ChatPromptTemplate
from pydantic import ValidationError
from apps.helper.logger import LoggerSingleton
from langgraph.graph import END
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
        self.MAX_RETRIES = 3 ## clean sau
        self.parser = JsonOutputParser()
        feild_des = "\n".join(f"- {name}: {field.description}" for name, field in Topic.model_fields.items())
        self.prompt = ChatPromptTemplate([
            ("system", f"""You are an instructional designer. 
                Given a Module json, generate a JSON array of topics that together allow a learner to achieve the aims. 
                Extract the following fields and ONLY return valid JSON matching the schema:
                {feild_des}
                Important:
                - Field quiz must be []. It will be filled by another agent.
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
        self.logger.info(f"[{self.agent_name}] is running...")     
        messages = state.get("messages", [])
        learningProgress: LearningProgress = state.get("learningProgress")  
        
        ## CHECK_INPUT
        idx_module = state.get("idx_module", None)
        if idx_module is None:
            self.logger.info("Graph signaled awaiting_input -> breaking astream to return to client")
            messages.append(("sys", "Please input idx_module"))
            return {
                "messages": messages,
                "next_agent": "END"
            }
        ## EXIT
        if state.get("exit_graph") is not None and state.get("exit_graph"):
            messages.append(("human", f"At {self.agent_name}. Exit Graph"))
            thread_id = state.get("thread_id")
            self.tools["save_state"](state, thread_id)
            return {
                "messages": messages ,
                "exit_graph": None,
                "next_agent": "END"
            }
  
        ## MAIN         
        try:
            try:
                idx = state.get("idx_module")
                module = learningProgress.modules[idx]
                messages.append(("human", f"Index selected module: {idx}"))
            except Exception as e:
                self.logger.error(f"Invalid selection: {state.get('idx_module')}")
                raise ValueError(f"Invalid selection: {state.get('idx_module')}") from e

            ## check_history
            if module.topics is not None and module.topics != []:
                messages.append(("sys", f"Load data {self.agent_name} is sucess"))
                return {
                    "learningProgress": learningProgress,
                    "messages": messages,
                    "idx_module": idx
                }
                
            prompt_inputs = {
                "module_json": module.model_dump_json(),
                "format_instructions": self.parser.get_format_instructions()
            }
            module.topics = self.invoke_chain(prompt_inputs, messages)

            self.tools["save_raw_output"](f"Module_selected{idx}_output.json", module.model_dump_json(indent=2))
            messages.append(("ai", f"Analysis Module: {module}"))

            self.logger.info(f"[{self.agent_name}] completed successfully.")
            return {
                "learningProgress": learningProgress,
                "messages": messages,
                "idx_module": idx
            }

        except Exception as e:
            self.logger.error(f"[{self.agent_name}] failed: {e}")
            raise ValueError(f"[{self.agent_name}] failed: {e}")
        
        
    def invoke_chain(self, prompt_inputs: dict, messages: list) -> list[Topic]:
        
        chain = self.prompt | self.llm 
        raw = chain.invoke(prompt_inputs)
        text = getattr(raw, "content", None) or getattr(raw, "text", None) or str(raw)
        text = text.strip()
        array_parsed_dict = []
        topics : list[Topic] = None
        
        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                array_parsed_dict = self.parser.parse(text)
                topics = [Topic(**topic) for topic in array_parsed_dict]
                return topics
            except (ValidationError, ValueError) as e:
                if attempt < self.MAX_RETRIES:
                    self.logger.debug(f"Validation failed, retrying {attempt}/{self.MAX_RETRIES}...")
                    raw = chain.invoke(prompt_inputs)
                    text = getattr(raw, "content", None) or getattr(raw, "text", None) or str(raw)
                    text = text.strip()
                else:
                    messages.append(("ai", f"Failed to parse Analysis Module after {self.MAX_RETRIES} attempts. Error: {e}"))
                    break

        return topics
    
        