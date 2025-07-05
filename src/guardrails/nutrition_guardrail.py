from typing import Any, Optional
from agents import Agent, GuardrailFunctionOutput, RunContextWrapper, Runner, TResponseInputItem, input_guardrail, output_guardrail
from pydantic import BaseModel

from src.context import UserSessionContext


class NutritionInput(BaseModel):
    is_nutrition_request: bool
    reasoning: str
    medical_condition: Optional[str] = None
    severity: Optional[str] = None


class MedicalMealPlanOutput(BaseModel):
    is_valid_plan: bool
    reasoning: str
    condition_covered: bool
    safety_notes_present: bool


nutrition_input_guardrail_agent = Agent(
    name="Nutrition Input Guardrail",
    instructions=(
        "Determine if the user's input is related to nutrition, dietary needs, or medical conditions "
        "that require specialized dietary guidance. Look for keywords and phrases such as: "
        "- Medical conditions: 'diabetes', 'celiac', 'gluten intolerance', 'hypertension', 'allergies' "
        "- Dietary restrictions: 'can't eat', 'allergic to', 'sensitive to', 'intolerant to' "
        "- Nutrition concerns: 'blood sugar', 'blood pressure', 'digestive issues', 'food allergies' "
        "- Special diets: 'medical diet', 'therapeutic diet', 'prescribed diet' "
        "If the input is not a nutrition request, explain why. "
        "If it is valid, identify the medical condition and severity level."
    ),
    output_type=NutritionInput,
    model="gemini-2.0-flash"
)


@input_guardrail
async def nutrition_input_guardrail(
    ctx: RunContextWrapper[UserSessionContext],
    agent: Agent,
    input: str | list[TResponseInputItem],
) -> GuardrailFunctionOutput:
    
    result = await Runner.run(nutrition_input_guardrail_agent, input, context=ctx.context)
    output = result.final_output_as(NutritionInput)
    
    return GuardrailFunctionOutput(
        output_info=output.reasoning,
        tripwire_triggered=not output.is_nutrition_request
    )



medical_meal_plan_output_guardrail_agent = Agent(
    name="Medical Meal Plan Output Guardrail",
    instructions=(
        "Validate that the generated medical meal plan is appropriate and safe for the user's condition. "
        "Check that: "
        "- The plan addresses the specific medical condition "
        "- Safety notes and disclaimers are included "
        "- The plan follows medical dietary guidelines "
        "- All meals are appropriate for the condition "
        "- The plan includes proper nutritional guidance "
        "If the plan is not valid or safe, explain the issues."
    ),
    output_type=MedicalMealPlanOutput,
    model="gemini-2.0-flash"
)


@output_guardrail
async def medical_meal_plan_output_guardrail(
    ctx: RunContextWrapper[UserSessionContext],
    agent: Agent,
    output: Any,
) -> GuardrailFunctionOutput:
    
    # # Check if output contains medical meal plan
    # if not isinstance(output, dict) or "medical_meal_plan" not in output:
    #     return GuardrailFunctionOutput(
    #         output_info="Output does not contain a medical meal plan",
    #         tripwire_triggered=True
    #     )
    
    result = await Runner.run(
        medical_meal_plan_output_guardrail_agent, 
        str(output), 
        context=ctx.context
    )
    output = result.final_output_as(MedicalMealPlanOutput)
    
    return GuardrailFunctionOutput(
        output_info=output.reasoning,
        tripwire_triggered=not output.is_valid_plan
    )


