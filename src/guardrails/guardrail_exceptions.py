"""
Simple Guardrail Exception Handler
Handles InputGuardrailTripwireTriggered and OutputGuardrailTripwireTriggered exceptions
"""

import time
from datetime import datetime
import logfire
from colorama import Fore, Style

from src.hooks import AgentLog


def handle_guardrail_exception(exception: Exception, user_input: str, agent_name: str, session_id: str, session_duration: float, user_name: str, user_uid: str) -> str:
    """
    Simple handler for guardrail exceptions
    
    Args:
        exception: The guardrail exception
        user_input: The user's input that triggered the guardrail
        agent_name: Name of the agent
        session_id: Session identifier
        session_duration: Session duration in seconds
        user_name: User's name
        user_uid: User's UID
        
    Returns:
        User-friendly message explaining the issue
    """
    
    # Log the violation
    violation_log = AgentLog(
        trace_id=session_id,
        agent_name=agent_name,
        event_type="GUARDRAIL_VIOLATION",
        user_name=user_name,
        user_uid=user_uid,
        timestamp=datetime.now().isoformat(),
        session_duration=session_duration,
        metadata={
            "exception_type": type(exception).__name__,
            "user_input": user_input,
            "error_message": str(exception),
            "session_duration": session_duration
        }
    )
    
    logfire.log(
        "warning",
        msg_template=f"Guardrail violation: {type(exception).__name__}",
        attributes=violation_log.model_dump()
    )
    
    # Simple user-friendly message
    if "Input" in type(exception).__name__:
        return (
            f"I need a bit more information to help you properly. "
            f"Could you please rephrase your question to focus on health, fitness, nutrition, or wellness topics? "
            f"For example, you could ask about workout plans, meal planning, setting fitness goals, or health advice."
        )
    elif "Output" in type(exception).__name__:
        return (
            f"I need to review my response to ensure it meets our quality standards. "
            f"Please give me a moment to provide you with better information."
        )
    else:
        return (
            f"I encountered an issue while processing your request. "
            f"Please try rephrasing your question or ask for help with a different health and wellness topic."
        ) 