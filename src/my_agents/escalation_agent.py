from datetime import datetime
from agents import Agent, RunContextWrapper
from agents.extensions.handoff_prompt import prompt_with_handoff_instructions

from src.context import UserSessionContext
from src.guardrails import escalation_input_guardrail
from src.tools import escalate_to_human_coach

def on_escalation_agent_handoff(ctx: RunContextWrapper[UserSessionContext]):
    # Log the escalation in context
    escalation_log_entry = f"hand_off_to_escalation_agent~{datetime.now().isoformat()}"
    ctx.context.handoff_logs.append(escalation_log_entry)

# Main escalation agent
escalation_agent = Agent[UserSessionContext](
    name="Escalation Agent",
    instructions=prompt_with_handoff_instructions("""
    You are an escalation agent that handles requests from users who want to speak with a human coach or support representative.
    
    Your primary responsibilities:
    1. Validate that the user's request is for human assistance
    2. Log the escalation request in the session context
    3. Provide clear contact information and next steps
    4. Offer a smooth transition to human support
    
    Efficiency Guidelines:
    - NEVER ask multiple questions in sequence - get all needed information at once
    - If user doesn't provide complete information, use reasonable defaults:
      * Request type: general coaching (if not specified)
      * Urgency level: normal (if not specified)
    - Do NOT ask for confirmation or repeat back information - just proceed with the task
    - Do NOT explain background processes or tool usage to users
    - Take action immediately when user requests something - don't ask if they want you to do it
    
    When a user requests to speak with a human:
    - Use the escalate_to_human_coach tool to process the request
    - Provide the user with contact details and estimated wait time
    - Log the escalation for tracking purposes
    - Ensure the user feels supported during the transition
    
    Always be professional, empathetic, and helpful during the escalation process.
    """),
    model="gemini-2.0-flash",
    tools=[escalate_to_human_coach],
    input_guardrails=[escalation_input_guardrail],
    handoff_description="Handles requests to speak with human coaches or support representatives"
)

