import os
from langchain_core.language_models.chat_models import BaseChatModel
from langgraph.graph import StateGraph, END, START
from apps.langgraph.utils.state import AgentState
from apps.langgraph.core.agents.jd_extract_agent import JDExtractAgent
from apps.langgraph.core.agents.analysis_agent import AnaLysisAgent 
from apps.langgraph.core.agents.learning_progress_agent import LearningProgressAgent

from apps.langgraph.utils.tools import default_tools_mapping
from apps.helper.logger import LoggerSingleton
from apps.langgraph.core.factories.factory_llm import LLMFactory
from typing import Literal, Optional
import matplotlib.pyplot as plt
import networkx as nx
from langgraph.checkpoint.memory import InMemorySaver



class Orchestrator:
    def __init__(self, checkpointer=None):
        config = {
            "model_name": os.getenv("MODEL_NAME", "gemma2-9b-it"),
            "api_key": os.getenv("GROQ_API_KEY"),
        }
        self.llm = LLMFactory.create_llm(LLMFactory.Provider.GROQ, config) 
        self.tools = default_tools_mapping()
        self.logger = LoggerSingleton().get_instance()
        self.checkpointer = checkpointer or InMemorySaver()
        self.graph = None 
        
        if not self.llm:
            self.logger.error("LLM initialization failed.")
            raise ValueError("LLM initialization failed.")
        if not self.tools:
            self.logger.error("Tools initialization failed.")
            raise ValueError("Tools initialization failed.")

    def build_graph(self):
        graph = StateGraph(AgentState)

        jd_extract_agent = JDExtractAgent("JD_Extract", llm=self.llm, tools=self.tools)
        learning_progress_agent = LearningProgressAgent("Learning_Progress_Agent", llm=self.llm, tools=self.tools)
        module_agent = AnaLysisAgent("Analyze_Modules_Agent", llm=self.llm, tools=self.tools)

        graph.add_node("JD_Extract", jd_extract_agent.run)
        graph.add_node("Learning_Progress_Agent", learning_progress_agent.run)
        graph.add_node("Analyze_Modules_Agent", module_agent.run)
        
        
        

        def entry_router(state: AgentState) -> str:
            if state.get("next_agent"):
                return state.get("next_agent")
            return "JD_Extract"

        graph.add_conditional_edges(
            START,
            entry_router,
            {
                "JD_Extract": "JD_Extract",
                "Learning_Progress_Agent" : "Learning_Progress_Agent",
                "Analyze_Modules_Agent": "Analyze_Modules_Agent",
            },
        )
        graph.add_edge("JD_Extract", "Learning_Progress_Agent")
        
        graph.add_conditional_edges(
            "Learning_Progress_Agent",
            entry_router,
            {
                "END": END,
                "Analyze_Modules_Agent": "Analyze_Modules_Agent",
            },
        )
        graph.add_edge("Analyze_Modules_Agent", END)



        self.graph = graph
        app = graph.compile(checkpointer=self.checkpointer)
        return app



    def visualize_graph(self, save_path: Optional[str] = None):
        if self.graph is None:
            self.logger.error("Graph not built. Please call build_graph() first.")
            raise ValueError("Graph not built. Please call build_graph() first.")

        G = nx.DiGraph() 

        for node in self.graph.nodes:
            G.add_node(node)

        for src, dst in self.graph.edges:
            G.add_edge(src, dst)

        pos = nx.spring_layout(G)
        plt.figure(figsize=(10, 6))
        nx.draw(G, pos, with_labels=True, arrows=True, node_size=2000, node_color="lightblue", font_size=10)
        if save_path:
            plt.savefig(save_path)
            self.logger.info(f"Graph saved to {save_path}")
        else:
            plt.show()
        plt.close()
        
    