import yaml
from typing import Dict, Any, Optional
from config.settings import settings
from src.utils.guardrails_setup import setup_guardrails_config, is_guardrails_configured

try:
    from guardrails import Guard
    from .unusual_prompt import UnusualPrompt
    from guardrails.hub import (
        DetectJailbreak,
        ValidLength,
        GibberishText
    )
    GUARDRAILS_AVAILABLE = True
except ImportError:
    GUARDRAILS_AVAILABLE = False

class SecurityGuards:
    def __init__(self):
        self.config = self._load_config()
        self.guardrails_enabled = self._setup_guardrails()
        self.input_guard = self._create_input_guard()
        self.output_guard = self._create_output_guard()
    
    def _setup_guardrails(self) -> bool:
        """Set up Guardrails configuration and check if it's available."""
        if not GUARDRAILS_AVAILABLE:
            print("⚠️  Guardrails not available. Security features will be limited.")
            return False
        
        if not is_guardrails_configured():
            if not setup_guardrails_config():
                print("⚠️  Failed to set up Guardrails. Security features will be limited.")
                return False
        
        return True
    
    def _load_config(self) -> Dict[str, Any]:
        try:
            with open(settings.guardrails_config, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"Guardrails config not found: {settings.guardrails_config}")
            return self._default_config()
    
    def _default_config(self) -> Dict[str, Any]:
        return {
            "guards": [
                {"name": "detect_jailbreak", "type": "detect_jailbreak", "enabled": True, "on_fail": "filter"},
                {"name": "unusual_prompt", "type": "prompt_injection", "enabled": True, "on_fail": "filter"},
            ],
            "input_validation": {"max_length": 2000, "min_length": 1},
            "output_validation": {"max_length": 4000, "check_relevance": True}
        }
    
    def _create_input_guard(self):
        if not self.guardrails_enabled:
            return None
            
        validators = []
        
        # Length validation
        input_config = self.config.get("input_validation", {})
        validators.append(ValidLength(
            min=input_config.get("min_length", 1),
            max=input_config.get("max_length", 2000),
            on_fail="reask"
        ))
        
        # Add enabled guards
        for guard_config in self.config.get("guards", []):
            if not guard_config.get("enabled", True):
                continue
                
            guard_type = guard_config.get("type")
            on_fail = guard_config.get("on_fail", "filter")
            
            if guard_type == "prompt_injection":
                validators.append(UnusualPrompt(on_fail=on_fail))
            elif guard_type == "detect_jailbreak":
                validators.append(DetectJailbreak(on_fail=on_fail))
        
        return Guard.from_string(validators=validators)
    
    def _create_output_guard(self):
        if not self.guardrails_enabled:
            return None
            
        validators = []
        
        # Length validation for output
        output_config = self.config.get("output_validation", {})
        validators.append(ValidLength(
            max=output_config.get("max_length", 4000),
            on_fail="reask"
        ))
        
        # Gibberish language check for output
        validators.append(GibberishText(threshold=0.5, on_fail="filter"))
        
        return Guard.from_string(validators=validators)
    
    def validate_input(self, user_input: str) -> Optional[str]:
        if not self.guardrails_enabled or not self.input_guard:
            return user_input  # Pass through if guardrails disabled
            
        try:
            result = self.input_guard.parse(user_input)
            
            # Log successful validation
            from src.utils.llm_logger import llm_logger
            llm_logger.log_validation_event(
                validator_name="input_guard",
                validation_type="input_validation",
                input_text=user_input,
                result="passed",
                threshold_met=True,
                details={"guard_type": "input", "validated_output_length": len(result.validated_output)}
            )
            
            return result.validated_output
        except Exception as e:
            print(f"Input validation failed: {e}")
            
            # Log failed validation
            from src.utils.llm_logger import llm_logger
            llm_logger.log_failed_validation(
                validator_name="input_guard",
                input_text=user_input,
                failure_reason=str(e)
            )
            
            llm_logger.log_validation_event(
                validator_name="input_guard",
                validation_type="input_validation",
                input_text=user_input,
                result="failed",
                threshold_met=False,
                details={"error": str(e), "guard_type": "input"}
            )
            
            return None
    
    def validate_output(self, output: str) -> Optional[str]:
        if not self.guardrails_enabled or not self.output_guard:
            return output  # Pass through if guardrails disabled
            
        try:
            result = self.output_guard.parse(output)
            
            # Log successful validation
            from src.utils.llm_logger import llm_logger
            llm_logger.log_validation_event(
                validator_name="output_guard",
                validation_type="output_validation",
                input_text=output,
                result="passed",
                threshold_met=True,
                details={"guard_type": "output", "validated_output_length": len(result.validated_output)}
            )
            
            return result.validated_output
        except Exception as e:
            print(f"Output validation failed: {e}")
            
            # Log failed validation
            from src.utils.llm_logger import llm_logger
            llm_logger.log_failed_validation(
                validator_name="output_guard",
                input_text=output,
                failure_reason=str(e)
            )
            
            llm_logger.log_validation_event(
                validator_name="output_guard",
                validation_type="output_validation",
                input_text=output,
                result="failed",
                threshold_met=False,
                details={"error": str(e), "guard_type": "output"}
            )
            
            return None
    
    def is_input_safe(self, user_input: str) -> bool:
        return self.validate_input(user_input) is not None
