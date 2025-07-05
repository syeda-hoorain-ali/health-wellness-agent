from datetime import datetime
from typing import Dict, Any, Optional
from agents import RunContextWrapper, function_tool
from pydantic import BaseModel

from src.context import UserSessionContext


# Escalation confirmation model
class EscalationConfirmation(BaseModel):
    escalation_id: str
    status: str = "escalated"
    contact_email: str = "coach@healthwellness.com"
    contact_phone: str = "+1-800-HEALTH-1"
    estimated_wait_time: str = "5-10 minutes"
    next_steps: str = "A human coach will contact you shortly to provide personalized guidance."


@function_tool(strict_mode=False)
async def escalate_to_human_coach(
    ctx: RunContextWrapper[UserSessionContext],
    request_type: Optional[str] = None,
    urgency_level: Optional[str] = "normal",
    additional_notes: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Escalates the user's request to a human coach or support representative.
    
    This function logs the escalation request, generates a unique escalation ID,
    and provides contact information for the user to connect with a human coach.
    The escalation is logged in the session context for tracking purposes.
    
    Args:
        request_type (Optional[str]): Type of escalation request (e.g., "coach", "support", "emergency").
        urgency_level (Optional[str]): Urgency level of the request ("low", "normal", "high", "emergency").
        additional_notes (Optional[str]): Any additional notes or context for the escalation.
    
    Returns:
        Dict[str, Any]: Escalation confirmation with contact details and next steps.
    """
    
    escalation_id = f"ESC-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{ctx.context.uid}"
    
    # Later i will add third party service to contact human
    # Like twilio, or something  else
    
    confirmation = EscalationConfirmation(
        escalation_id=escalation_id,
        status="escalated",
        contact_email="coach@healthwellness.com",
        contact_phone="+1-800-HEALTH-1",
        estimated_wait_time="5-10 minutes",
        next_steps="A human coach will contact you shortly to provide personalized guidance."
    )
    
    response = {
        "escalation_confirmation": confirmation.model_dump(),
        "user_name": ctx.context.name,
        "escalation_logged": True,
        "message": f"Hi {ctx.context.name}, I'm connecting you to a human coach now. Please wait while I transfer you.",
        "session_summary": {
            "total_handoffs": len(ctx.context.handoff_logs),
            "user_goal": ctx.context.goal.model_dump() if ctx.context.goal else None,
            "progress_updates": len(ctx.context.progress_logs)
        }
    }
    
    return response

