from typing import Dict, Any
from langgraph.graph import StateGraph, END
from typing_extensions import TypedDict
from .nodes import ChatbotPipeline

class ChatbotState(TypedDict):
    user_input: str
    validated_input: str
    context: str
    llm_response: str
    response: str
    error: str

class ChatbotGraph:
    def __init__(self):
        self.pipeline = ChatbotPipeline()
        self.graph = self._create_graph()
    
    def _create_graph(self) -> StateGraph:
        workflow = StateGraph(ChatbotState)
        
        # Add nodes
        workflow.add_node("input_validation", self.pipeline.input_validation_node)
        workflow.add_node("context_retrieval", self.pipeline.context_retrieval_node)
        workflow.add_node("llm_generation", self.pipeline.llm_generation_node)
        workflow.add_node("output_validation", self.pipeline.output_validation_node)
        
        # Define the flow
        workflow.set_entry_point("input_validation")
        
        # Add conditional edges
        workflow.add_conditional_edges(
            "input_validation",
            self._should_continue_after_validation,
            {
                "continue": "context_retrieval",
                "end": END
            }
        )
        
        workflow.add_edge("context_retrieval", "llm_generation")
        workflow.add_edge("llm_generation", "output_validation")
        workflow.add_edge("output_validation", END)
        
        return workflow.compile()
    
    def _should_continue_after_validation(self, state: ChatbotState) -> str:
        if "error" in state:
            return "end"
        return "continue"
    
    def process_message(self, user_input: str) -> str:
        initial_state = {"user_input": user_input}
        
        try:
            result = self.graph.invoke(initial_state)
            return result.get("response", "Customer service closed, go complain to someone else.")
        except Exception as e:
            return f"An error occurred: {str(e)}"
    
    def initialize_knowledge_base(self):
        self.pipeline.retriever.initialize_knowledge_base()
    
    def get_knowledge_base_info(self) -> Dict[str, Any]:
        return self.pipeline.retriever.get_knowledge_base_info()
