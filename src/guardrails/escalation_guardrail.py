from typing import Literal, Optional
from agents import Agent, GuardrailFunctionOutput, RunContextWrapper, Runner, TResponseInputItem, input_guardrail
from pydantic import BaseModel

from src.context import UserSessionContext


# Escalation request validation model
class EscalationRequestValidation(BaseModel):
    is_escalation_request: bool
    reasoning: str
    request_type: Optional[Literal["coach", "support", "emergency"]] = None


# Input guardrail for escalation requests
escalation_input_guardrail_agent = Agent(
    name="Escalation Input Guardrail",
    instructions=(
        "Determine if the user's input is a request to speak with a human coach, trainer, or support representative. "
        "Look for keywords and phrases such as: "
        "- 'speak to a human', 'talk to a coach', 'contact support' "
        "- 'real trainer', 'live coach', 'human assistance' "
        "- 'speak to someone', 'get help from a person' "
        "- 'emergency', 'urgent help needed' "
        "If the input is not an escalation request, explain why. "
        "If it is valid, categorize the type of escalation needed."
    ),
    output_type=EscalationRequestValidation,
    model="gemini-2.0-flash"
)


@input_guardrail
async def escalation_input_guardrail(
    ctx: RunContextWrapper[UserSessionContext],
    agent: Agent,
    input: str | list[TResponseInputItem],
) -> GuardrailFunctionOutput:
    
    result = await Runner.run(escalation_input_guardrail_agent, input, context=ctx.context)
    output = result.final_output_as(EscalationRequestValidation)
    
    return GuardrailFunctionOutput(
        output_info=output.reasoning,
        tripwire_triggered=not output.is_escalation_request
    )

