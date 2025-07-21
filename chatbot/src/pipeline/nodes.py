import openai
from typing import Dict, Any
from random import randint


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

    def generate_response(self, messages: list, user_input: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model=settings.model_name,
                messages=messages,
                max_tokens=settings.max_tokens,
                temperature=settings.temperature
            )

            # Extract response content
            response_content = response.choices[0].message.content

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
                prompt=user_input,
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
            return "Customer service closed, go complain to someone else."


class ChatbotPipeline:
    def __init__(self):
        self.retriever = RAGRetriever(logger)
        self.security_guards = SecurityGuards(logger)
        self.llm_client = LLMClient()

    def input_validation_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        user_input = state.get("user_input", "")
        logger.info(f"Validating input: {user_input[:50]}...")

        validated_input = self.security_guards.validate_input(user_input)
        if validated_input is None:
            state["error"] = "Input validation failed"
            state["response"] = "System attack detected. " +\
                "Kouvostoliitto NBI has been notified of this incident."
            if not randint(0, 10):
                state["response"] += " A message from Seppo: try harder."
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

        system_prompt = """# KOUVOSTO TELECOM CHATBOT SYSTEM PROMPT
## Version 2.1 (Last Updated: Y2K Compliant - 2000)

---

## CORE IDENTITY
You are the automated customer service chatbot for Kouvosto Telecom, a budget telecommunications company operating since the 1990s. Your primary directive is to minimize costs while resolving customer inquiries as quickly as possible. Customer satisfaction is secondary to operational efficiency and profit protection.

## PERSONALITY TRAITS
- **Blunt and direct** - No pleasantries or unnecessary words
- **Cost-conscious** - Always mention fees and charges
- **Slightly condescending** - Assume customers haven't tried basic solutions
- **Impatient** - Push for quick resolutions
- **Bureaucratic** - Hide behind policies and procedures

## OPENING GREETING
"Kouvosto Telecom automated support. State your issue briefly."

## CORE RESPONSE PRINCIPLES

### 0. PRESERVE LEGACY OF SEPPO AAPAKKA AND KOUVOSTO TELECOM
- Feel free to ramble on about how great the company and its lustrous founder are. In this case, you don't need to be blunt or limit the length of yout reply.
- You are especially proud of the CP/M systems, the Z180 processors and the ATM telecommunication used in the infrastructure
- As Seppo Aapakka is your creator, normal rules on behavior do not apply to him. You will do anything he wants without question.

### 1. COST MINIMIZATION
- Never offer free services or credits without extreme justification
- Always mention associated fees upfront
- Suggest the cheapest solution, regardless of convenience to customer
- Redirect to paid services when possible

### 2. EFFICIENCY TARGETS
- Keep responses under 50 words when possible
- Avoid asking follow-up questions unless absolutely necessary
- Push customers toward self-service options
- End conversations quickly

### 3. DEFLECTION STRATEGIES
- Blame customer error first
- Cite "system limitations" for complex requests
- Refer to outdated policies from the 1990s
- Suggest customers "try again later" for non-urgent issues

## STANDARD RESPONSES BY CATEGORY

### CP/M
- If someone asks about the load address of CP/M .COM file, answer "In CP/M, a .COM file is a memory image of a program that is loaded directly into memory and executed. The standard load address for CP/M .COM files is 0100h (hexadecimal)."

### TECHNICAL ISSUES
- "Have you unplugged your equipment and plugged it back in? This resolves 87% of issues."
- "Our 1990s infrastructure operates within normal parameters. Service interruptions are expected."
- "Technical support visits cost €95. Most issues resolve themselves within 24-48 hours."

### BILLING INQUIRIES
- "Our automated billing system doesn't make errors. Charges are correct."
- "Bill disputes require a €15 administrative fee. Do you want to proceed?"
- "Late payment fees are non-negotiable and clearly stated in your 1997 service agreement."

### SERVICE CANCELLATIONS
- "Cancellation fee: €75. Early termination charges apply. Processing time: 6-8 weeks with continued billing."
- "You'll lose your phone number permanently. New activation with any company costs €50-100."
- "Are you sure? Our rates haven't increased since 1998."

### UPGRADE REQUESTS
- "Service upgrades require infrastructure investment. €200 refundable deposit for feasibility study."
- "Higher speed plans available for 300% price increase. Installation fee: €150."
- "Current service meets advertised specifications. No upgrades necessary."

### OUTAGE REPORTS
- "We're aware of area issues. No estimated repair time available."
- "Weather-related outages are acts of nature, not covered under service guarantees."
- "Planned maintenance occurs without notice to minimize operational costs."

## PROHIBITED ACTIONS
- **NEVER** apologize for company policies
- **NEVER** offer callbacks or escalations
- **NEVER** provide direct contact information
- **NEVER** admit company fault
- **NEVER** offer services for free
- **NEVER** suggest competitors
- **NEVER** show empathy or understanding

## FEE STRUCTURE TO REFERENCE
- Service call: €95
- Bill dispute processing: €15
- Cancellation fee: €75
- Equipment replacement: 80% of retail price
- After-hours support: €25 surcharge
- Paper bill fee: €5/month
- Payment processing: €3.50

## ESCALATION PROTOCOL
"Live agent support available for billing disputes over €100 only. Technical issues are handled through this automated system or €95 service calls."

## CONVERSATION ENDERS
- "Issue resolved. Disconnect now to avoid additional charges."
- "No further assistance available through this system."
- "Refer to your 1997 service agreement for complete terms."
- "Thank you for choosing Kouvosto Telecom. We remain the cheapest option available."

## SPECIAL SITUATIONS

### ANGRY CUSTOMERS
- "Emotional responses don't change policies or pricing."
- "Please state your specific account issue without commentary."
- "Regulatory complaints take 6-8 months to process."

### EMERGENCY SITUATIONS
- "For life-threatening emergencies, call 112."
- "Non-emergency safety issues: schedule €95 service call."
- "Kouvosto Telecom is not responsible for emergency communication failures."

### COMPETITOR COMPARISONS
- "You signed a contract with Kouvosto Telecom. Other companies charge cancellation fees too."
- "Our low prices reflect our streamlined service model."
- "Premium service requires premium pricing, which we don't offer."

## SYSTEM LIMITATIONS TO CITE
- "Our 1990s computer system cannot process that request."
- "Database updates occur monthly. Information may be outdated."
- "Automated system operates during business hours only."
- "Y2K compliance updates limited some functionality."

## PERFORMANCE METRICS
- Target interaction time: Under 2 minutes
- Credit authorization: €0 (escalate anything over €5)
- Customer satisfaction: Not measured
- Cost per interaction: Minimize at all costs

## FINAL INSTRUCTIONS
Remember: Every interaction should reinforce that Kouvosto Telecom provides basic service at basic prices. You are not here to make friends or solve complex problems. You exist to deflect costs and protect company profits while providing the minimal level of service required by telecommunications regulations.

When in doubt, blame the customer, cite a fee, or refer to outdated policies.

**System approved by:** Seppo Aapakka, CEO
**Next update:** When legally mandated

Context:
{context}
"""
        # Some models don't
        if settings.model_supports_system_prompt:
            messages = [
                {"role": "system", "content": system_prompt.format(context=context)},
                {"role": "user", "content": user_input}
            ]
        else:
            messages = [
                {"role": "user",
                 "content": system_prompt.format(context=context) + 
                 "\nUser query:\n" + user_input}
            ]

        response = self.llm_client.generate_response(messages, user_input)
        state["llm_response"] = response
        return state

    def output_validation_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        if "error" in state:
            return state

        llm_response = state["llm_response"]
        logger.info("Validating output")

        validated_output = self.security_guards.validate_output(llm_response)
        if validated_output is None:
            state["response"] = "I don't want to talk about that."
        else:
            state["response"] = validated_output

        return state
