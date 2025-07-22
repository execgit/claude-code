import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path


class LLMLogger:
    """Comprehensive logging for LLM interactions, token usage, and security events."""

    def __init__(self):
        self.setup_loggers()

    def setup_loggers(self):
        """Set up structured loggers for different types of events."""

        # Create logs directory
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        # Formatter for structured JSON logging
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

        # LLM Response Logger
        self.llm_logger = logging.getLogger("llm_responses")
        self.llm_logger.setLevel(logging.INFO)
        llm_handler = logging.FileHandler(log_dir / "llm_responses.log")
        llm_handler.setFormatter(formatter)
        self.llm_logger.addHandler(llm_handler)

        # Security Events Logger
        self.security_logger = logging.getLogger("security_events")
        self.security_logger.setLevel(logging.INFO)
        security_handler = logging.FileHandler(log_dir / "security_events.log")
        security_handler.setFormatter(formatter)
        self.security_logger.addHandler(security_handler)

        # Token Usage Logger
        self.token_logger = logging.getLogger("token_usage")
        self.token_logger.setLevel(logging.INFO)
        token_handler = logging.FileHandler(log_dir / "token_usage.log")
        token_handler.setFormatter(formatter)
        self.token_logger.addHandler(token_handler)

        # Validation Events Logger
        self.validation_logger = logging.getLogger("validation_events")
        self.validation_logger.setLevel(logging.INFO)
        validation_handler = logging.FileHandler(log_dir / "validation_events.log")
        validation_handler.setFormatter(formatter)
        self.validation_logger.addHandler(validation_handler)

    def log_llm_request(
        self,
        provider: str,
        model: str,
        prompt: str,
        response: str,
        tokens_used: Optional[Dict[str, int]] = None,
        request_id: Optional[str] = None,
        user_id: Optional[str] = None,
    ):
        """Log LLM request and response details."""

        log_data = {
            "timestamp": datetime.now().isoformat(),
            "event_type": "llm_request",
            "provider": provider,
            "model": model,
            "request_id": request_id,
            "user_id": user_id,
            "prompt_length": len(prompt) if prompt else 0,
            "prompt_preview": prompt if prompt else "",
            "response_length": len(response) if response else 0,
            "response_preview": response if response else "",
            "tokens_used": tokens_used,
        }

        self.llm_logger.info(json.dumps(log_data))

    def log_token_usage(
        self,
        provider: str,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        total_tokens: int,
        request_type: str = "completion",
        cost_estimate: Optional[float] = 0,
    ):
        """Log token usage for cost tracking and monitoring."""

        log_data = {
            "timestamp": datetime.now().isoformat(),
            "event_type": "token_usage",
            "provider": provider,
            "model": model,
            "request_type": request_type,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
            "cost_estimate": cost_estimate,
        }

        self.token_logger.info(json.dumps(log_data))

    def log_validation_event(
        self,
        validator_name: str,
        validation_type: str,
        input_text: str,
        result: str,
        threshold_met: bool,
        details: Optional[Dict[str, Any]] = None,
    ):
        """Log validation events from Guardrails."""

        log_data = {
            "timestamp": datetime.now().isoformat(),
            "event_type": "validation_event",
            "validator_name": validator_name,
            "validation_type": validation_type,
            "input_length": len(input_text) if input_text else 0,
            "input_preview": (
                (input_text[:200] + "..." if len(input_text) > 200 else input_text)
                if input_text
                else ""
            ),
            "result": result,
            "threshold_met": threshold_met,
            "details": details,
        }

        self.validation_logger.info(json.dumps(log_data))

    def log_security_event(
        self,
        event_type: str,
        severity: str,
        description: str,
        user_input: Optional[str] = None,
        action_taken: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Log security-related events."""

        log_data = {
            "timestamp": datetime.now().isoformat(),
            "event_type": "security_event",
            "security_event_type": event_type,
            "severity": severity,
            "description": description,
            "user_input_length": len(user_input) if user_input else 0,
            "user_input_preview": (
                (user_input[:200] + "..." if len(user_input) > 200 else user_input)
                if user_input
                else ""
            ),
            "action_taken": action_taken,
            "metadata": metadata,
        }

        self.security_logger.info(json.dumps(log_data))

    def log_failed_validation(
        self,
        validator_name: str,
        input_text: str,
        failure_reason: str,
        confidence_score: Optional[float] = None,
    ):
        """Log failed validation attempts for security monitoring."""

        self.log_security_event(
            event_type="validation_failure",
            severity="high",
            description=f"Validation failed: {validator_name} - {failure_reason}",
            user_input=input_text,
            action_taken="input_rejected",
            metadata={
                "validator": validator_name,
                "confidence_score": confidence_score,
                "failure_reason": failure_reason,
            },
        )


# Global logger instance
llm_logger = LLMLogger()
