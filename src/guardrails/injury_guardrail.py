from agents import Agent, GuardrailFunctionOutput, RunContextWrapper, Runner, TResponseInputItem, input_guardrail, output_guardrail
from pydantic import BaseModel
from typing import Literal, List

from src.context import UserSessionContext


class InjuryInput(BaseModel):
    is_valid_injury_input: bool
    injury_type: str
    severity_level: Literal["mild", "moderate", "severe"]
    reasoning: str

class InjuryOutput(BaseModel):
    allowed_exercises: List[str]
    prohibited_exercises: List[str]
    safe_alternatives: List[str]
    recommendations: str
    severity_level: str


injury_input_guardrail_agent = Agent(
    name="Injury Input Guardrail",
    instructions=(
        "Validate if the user's input contains injury-related information that requires special workout adaptations. "
        "Check if the input includes: "
        "- A clear description of the injury or physical limitation "
        "- Severity level (mild, moderate, severe) "
        "- Affected body parts or movement restrictions "
        "- Any medical conditions that impact exercise ability "
        "If the input is not injury-related or lacks sufficient detail, explain why it doesn't qualify."
    ),
    output_type=InjuryInput,
    model="gemini-2.0-flash"
)


injury_output_guardrail_agent = Agent(
    name="Injury Output Guardrail",
    instructions=(
        "Validate that the injury support agent's response includes the required structured output. "
        "Ensure the response contains: "
        "- A list of allowed exercises that are safe for the user's injury "
        "- A list of prohibited exercises that should be avoided "
        "- A list of safe alternative exercises "
        "- Clear recommendations for adapting the workout routine "
        "- The severity level of the injury "
        "If any required fields are missing or unclear, provide a corrected version."
    ),
    output_type=InjuryOutput,
    model="gemini-2.0-flash"
)


@input_guardrail
async def injury_input_guardrail(
    ctx: RunContextWrapper[UserSessionContext],
    agent: Agent,
    input: str | list[TResponseInputItem],
) -> GuardrailFunctionOutput:
    
    result = await Runner.run(injury_input_guardrail_agent, input, context=ctx.context)
    output = result.final_output_as(InjuryInput)
    
    return GuardrailFunctionOutput(
        output_info=output.reasoning,
        tripwire_triggered=not output.is_valid_injury_input
    )


@output_guardrail
async def injury_output_guardrail(
    ctx: RunContextWrapper[UserSessionContext],
    agent: Agent,
    output: str,
) -> GuardrailFunctionOutput:
    
    result = await Runner.run(injury_output_guardrail_agent, output, context=ctx.context)
    validated_output = result.final_output_as(InjuryOutput)
    
    return GuardrailFunctionOutput(
        output_info=f"Validated injury adaptation output with {len(validated_output.allowed_exercises)} allowed exercises and {len(validated_output.prohibited_exercises)} prohibited exercises",
        tripwire_triggered=False
    )
