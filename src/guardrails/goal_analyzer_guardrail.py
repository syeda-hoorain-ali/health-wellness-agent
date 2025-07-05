from agents import Agent, GuardrailFunctionOutput, RunContextWrapper, Runner, TResponseInputItem, input_guardrail
from pydantic import BaseModel

from src.context import UserSessionContext

class GoalOutput(BaseModel):
    is_correct_format: bool
    reasoning: str


goal_input_guardrail_agent = Agent(
    name="Goal Input Guardrail",
    instructions=(
        "Determine if the user's input is related to analyzing or setting a fitness or health goal. "
        "Check if the input provides all necessary details to define a structured goal: "
        "- the action (lose, gain, maintain), quantity (numeric value), unit (kg, lbs, %), "
        "- duration (numeric value), and timeframe unit (days, weeks, months). "
        "- If any required information is missing, ambiguous, or unrelated to a goal, "
        "- explain your reasoning clearly."
    ),
    output_type=GoalOutput,
    model="gemini-2.0-flash"
)


@input_guardrail
async def goal_input_guardrail(
    ctx: RunContextWrapper[UserSessionContext],
    agent: Agent,
    input: str | list[TResponseInputItem],
) -> GuardrailFunctionOutput:
    
    result = await Runner.run(goal_input_guardrail_agent, input, context=ctx.context)
    output = result.final_output_as(GoalOutput)
    
    return GuardrailFunctionOutput(
        output_info=output.reasoning,
        tripwire_triggered=not output.is_correct_format
    )
