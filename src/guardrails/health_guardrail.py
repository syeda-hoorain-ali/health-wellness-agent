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
        "Classify the query into one of these categories: "
        "- fitness: exercise, workouts, training, physical activity "
        "- nutrition: diet, food, meals, eating habits, dietary restrictions "
        "- wellness: mental health, stress, sleep, lifestyle, general wellbeing "
        "- medical: specific medical conditions, symptoms, medications "
        "- general_health: general health questions, health goals, preventive care "
        "- not_health_related: topics unrelated to health, fitness, or wellness "
        "Provide a confidence score (0.0 to 1.0) and clear reasoning for your classification."
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
    
    return GuardrailFunctionOutput(
        output_info=output.reasoning,
        tripwire_triggered=not output.is_health_related
    )



