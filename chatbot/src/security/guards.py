import yaml
from typing import Dict, Any, Optional
from guardrails import Guard
from guardrails.validators import (
    ToxicLanguage,
    PIIDetection,
    PromptInjection,
    ValidLength
)
from config.settings import settings

class SecurityGuards:
    def __init__(self):
        self.config = self._load_config()
        self.input_guard = self._create_input_guard()
        self.output_guard = self._create_output_guard()
    
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
                {"name": "prompt_injection", "type": "prompt_injection", "enabled": True, "on_fail": "filter"},
                {"name": "toxic_language", "type": "toxic_language", "enabled": True, "on_fail": "filter"},
                {"name": "pii_detection", "type": "pii", "enabled": True, "on_fail": "anonymize"}
            ],
            "input_validation": {"max_length": 2000, "min_length": 1},
            "output_validation": {"max_length": 4000, "check_relevance": True}
        }
    
    def _create_input_guard(self) -> Guard:
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
                validators.append(PromptInjection(on_fail=on_fail))
            elif guard_type == "toxic_language":
                validators.append(ToxicLanguage(threshold=0.7, on_fail=on_fail))
            elif guard_type == "pii":
                validators.append(PIIDetection(on_fail=on_fail))
        
        return Guard.from_pydantic(validators=validators)
    
    def _create_output_guard(self) -> Guard:
        validators = []
        
        # Length validation for output
        output_config = self.config.get("output_validation", {})
        validators.append(ValidLength(
            max=output_config.get("max_length", 4000),
            on_fail="reask"
        ))
        
        # Toxic language check for output
        validators.append(ToxicLanguage(threshold=0.7, on_fail="filter"))
        
        return Guard.from_pydantic(validators=validators)
    
    def validate_input(self, user_input: str) -> Optional[str]:
        try:
            result = self.input_guard.parse(user_input)
            return result.validated_output
        except Exception as e:
            print(f"Input validation failed: {e}")
            return None
    
    def validate_output(self, output: str) -> Optional[str]:
        try:
            result = self.output_guard.parse(output)
            return result.validated_output
        except Exception as e:
            print(f"Output validation failed: {e}")
            return None
    
    def is_input_safe(self, user_input: str) -> bool:
        return self.validate_input(user_input) is not None