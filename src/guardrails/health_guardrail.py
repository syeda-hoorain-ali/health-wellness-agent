from agents import Agent, GuardrailFunctionOutput, RunContextWrapper, Runner, TResponseInputItem, input_guardrail
from pydantic import BaseModel
from typing import Literal

from src.context import UserSessionContext


class HealthQueryValidation(BaseModel):
    is_health_related: bool
    query_category: Literal["fitness", "nutrition", "wellness", "medical", "general_health", "not_health_related"]
    confidence_score: float
    reasoning: str


health_input_guardrail_agent = Agent(
    name="Health Input Guardrail",
    instructions=(
        "Determine if the user's input is related to health, fitness, nutrition, or wellness topics. "
        "Be INCLUSIVE and classify health-related queries into these categories: "
        "- fitness: exercise, workouts, training, physical activity, gym, running, sports "
        "- nutrition: diet, food, meals, eating habits, dietary restrictions, meal planning, calories "
        "- wellness: mental health, stress, sleep, lifestyle, general wellbeing, mindfulness, meditation "
        "- medical: specific medical conditions, symptoms, medications, health appointments, checkups "
        "- general_health: general health questions, health goals, preventive care, scheduling appointments, "
        "  progress tracking, health monitoring, check-ins, reminders, health planning "
        "- not_health_related: topics completely unrelated to health, fitness, or wellness "
        
        "IMPORTANT: The following are ALWAYS health-related and should be classified as general_health: "
        "- Scheduling appointments, check-ins, or reminders "
        "- Progress tracking and monitoring "
        "- Health goal setting and planning "
        "- Wellness coaching and support requests "
        "- Any request related to the user's health journey or wellness program "
        
        "Provide a confidence score (0.0 to 1.0) and clear reasoning for your classification. "
        "When in doubt, classify as health-related rather than not_health_related."
    ),
    output_type=HealthQueryValidation,
    model="gemini-2.0-flash"
)


@input_guardrail
async def health_input_guardrail(
    ctx: RunContextWrapper[UserSessionContext],
    agent: Agent,
    input: str | list[TResponseInputItem],
) -> GuardrailFunctionOutput:
    
    result = await Runner.run(health_input_guardrail_agent, input, context=ctx.context)
    output = result.final_output_as(HealthQueryValidation)
    
    # Log the classification for debugging
    print(f"Health Guardrail Classification: {output.query_category} (confidence: {output.confidence_score})")
    print(f"Reasoning: {output.reasoning}")
    
    # Only trigger tripwire if confidence is high and it's clearly not health-related
    tripwire_triggered = (
        not output.is_health_related and 
        output.confidence_score > 0.8 and 
        output.query_category == "not_health_related"
    )
    
    return GuardrailFunctionOutput(
        output_info=f"Classified as: {output.query_category} (confidence: {output.confidence_score}). {output.reasoning}",
        tripwire_triggered=tripwire_triggered
    )


