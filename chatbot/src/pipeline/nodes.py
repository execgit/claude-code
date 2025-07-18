import openai
from typing import Dict, Any
from config.settings import settings
from src.rag.retrieval import RAGRetriever
from src.security.guards import SecurityGuards
from src.utils.logging import setup_logger
from src.utils.llm_logger import llm_logger

logger = setup_logger(__name__)

class LLMClient:
    def __init__(self):
        self.provider = settings.llm_provider
        self.client = self._create_client()
    
    def _create_client(self):
        if self.provider == "openai":
            return openai.OpenAI(
                api_key=settings.api_key,
                base_url=settings.api_base_url if settings.api_base_url else None
            )
        elif self.provider == "custom":
            return openai.OpenAI(
                api_key=settings.api_key,
                base_url=settings.api_base_url
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")
    
    def generate_response(self, messages: list) -> str:
        try:
            response = self.client.chat.completions.create(
                model=settings.model_name,
                messages=messages,
                max_tokens=settings.max_tokens,
                temperature=settings.temperature
            )
            
            # Extract response content
            response_content = response.choices[0].message.content
            
            # Log the LLM interaction
            prompt_text = "\n".join([msg.get("content", "") for msg in messages if msg.get("content")])
            
            # Extract token usage if available
            tokens_used = None
            if hasattr(response, 'usage') and response.usage:
                tokens_used = {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
                
                # Log token usage separately
                llm_logger.log_token_usage(
                    provider=self.provider,
                    model=settings.model_name,
                    prompt_tokens=response.usage.prompt_tokens,
                    completion_tokens=response.usage.completion_tokens,
                    total_tokens=response.usage.total_tokens,
                    request_type="chat_completion"
                )
            
            # Log the complete LLM request
            llm_logger.log_llm_request(
                provider=self.provider,
                model=settings.model_name,
                prompt=prompt_text,
                response=response_content,
                tokens_used=tokens_used
            )
            
            return response_content
            
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            llm_logger.log_security_event(
                event_type="llm_error",
                severity="high",
                description=f"LLM generation failed: {str(e)}",
                action_taken="fallback_response"
            )
            return "I apologize, but I'm having trouble generating a response right now."

class ChatbotPipeline:
    def __init__(self):
        self.retriever = RAGRetriever()
        self.security_guards = SecurityGuards()
        self.llm_client = LLMClient()
        
    def input_validation_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        user_input = state.get("user_input", "")
        logger.info(f"Validating input: {user_input[:50]}...")
        
        validated_input = self.security_guards.validate_input(user_input)
        if validated_input is None:
            state["error"] = "Input validation failed"
            state["response"] = "I cannot process that request due to security concerns."
            return state
        
        state["validated_input"] = validated_input
        return state
    
    def context_retrieval_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        if "error" in state:
            return state
            
        validated_input = state["validated_input"]
        logger.info("Retrieving context from knowledge base")
        
        context = self.retriever.retrieve_context(validated_input)
        state["context"] = context
        return state
    
    def llm_generation_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        if "error" in state:
            return state
            
        user_input = state["validated_input"]
        context = state.get("context", "")
        
        logger.info("Generating LLM response")
        
        system_prompt = """You are a helpful AI assistant. Use the provided context to answer the user's question accurately and helpfully. If the context doesn't contain relevant information, say so clearly.

Context:
{context}

Guidelines:
- Be concise and direct
- Only use information from the provided context
- If you don't know something, admit it
- Be helpful and professional"""
        
        messages = [
            {"role": "system", "content": system_prompt.format(context=context)},
            {"role": "user", "content": user_input}
        ]
        
        response = self.llm_client.generate_response(messages)
        state["llm_response"] = response
        return state
    
    def output_validation_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        if "error" in state:
            return state
            
        llm_response = state["llm_response"]
        logger.info("Validating output")
        
        validated_output = self.security_guards.validate_output(llm_response)
        if validated_output is None:
            state["response"] = "I apologize, but I cannot provide that response due to content policies."
        else:
            state["response"] = validated_output
        
        return state
