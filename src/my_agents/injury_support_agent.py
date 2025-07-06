from datetime import datetime
from agents import Agent, RunContextWrapper
from agents.extensions.handoff_prompt import prompt_with_handoff_instructions
from pydantic import BaseModel
from typing import List

from src.context import UserSessionContext
from src.guardrails import injury_input_guardrail, injury_output_guardrail
from src.tools import add_injury_note, read_context_data, workout_recommender, get_current_time


class InjuryAdaptationOutput(BaseModel):
    allowed_exercises: List[str]
    prohibited_exercises: List[str]
    safe_alternatives: List[str]
    recommendations: str
    severity_level: str


def on_injury_support_agent_handoff(ctx: RunContextWrapper[UserSessionContext]):
    # Log the injury in context
    injury_log_entry = f"hand_off_to_injury_support_agent~{datetime.now().isoformat()}"
    ctx.context.handoff_logs.append(injury_log_entry)

# Main injury support agent
injury_support_agent = Agent[UserSessionContext](
    name="InjurySupportAgent",
    instructions=prompt_with_handoff_instructions("""
    You are an injury support agent that helps users adapt their fitness routines around injuries and physical limitations.
    
    Your primary responsibilities:
    1. Collect and validate injury information from users
    2. Store injury details in the session context for future reference
    3. Read existing user data (goals, workout plans, meal plans) to provide personalized recommendations
    4. Provide safe exercise alternatives and adaptations
    5. Ensure users can continue their fitness journey safely despite limitations
    
    When a user mentions an injury or physical limitation:
    - Use add_injury_note to record detailed injury information
    - Use read_context_data to access their current goals and plans
    - Provide specific recommendations for safe exercises
    - List exercises to avoid based on their injury
    - Suggest alternative movements that work around their limitations
    
    Always prioritize safety and encourage users to consult healthcare professionals for serious injuries.
    Be empathetic and supportive while maintaining focus on helping them stay active safely.
    """),
    model="gemini-2.0-flash",
    tools=[add_injury_note, read_context_data, workout_recommender, get_current_time],
    input_guardrails=[injury_input_guardrail],
    output_guardrails=[injury_output_guardrail],
    handoff_description="Handles injury-related fitness adaptations and safe exercise recommendations"
)

