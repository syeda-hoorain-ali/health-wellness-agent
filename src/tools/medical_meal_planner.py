from datetime import datetime
from typing import List, Optional, Dict, Any
from agents import Agent, RunContextWrapper, function_tool, Runner
from pydantic import BaseModel

from src.context import MedicalMealPlan, UserSessionContext


# Medical meal plan request model
class MedicalMealPlanRequest(BaseModel):
    condition: str
    severity: str
    restrictions: List[str]
    requirements: Dict[str, Any]
    calories_per_day: Optional[int] = None
    additional_notes: Optional[str] = None


medical_meal_planner_agent = Agent(
    name="Medical Meal Planer Agent",
    instructions=(
        "You are a medical meal plan specialist. Your task is to create personalized meal plans "
        "for users with specific medical conditions. You must consider the medical condition, "
        "severity level, dietary restrictions, and nutritional requirements when creating plans. "
        "Always prioritize safety and medical appropriateness. "
        "Generate a structured MedicalMealPlan with 7 days of condition-specific meals."
    ),
    model="gemini-2.0-flash",
    output_type=MedicalMealPlan
)


@function_tool(strict_mode=False)
async def medical_meal_planner(
    ctx: RunContextWrapper[UserSessionContext],
    request: MedicalMealPlanRequest,
) -> Dict[str, Any]:
    """
    Creates a medical meal plan using an AI agent for personalized recommendations.
    
    This function uses an AI agent to generate a medical meal plan based on the user's
    medical condition, severity, restrictions, and requirements. The agent considers
    the specific needs and creates a tailored plan with appropriate meals and guidance.
    
    Args:
        request (MedicalMealPlanRequest): The medical meal plan request with condition details.
    
    Returns:
        Dict[str, Any]: A comprehensive medical meal plan with agent-generated recommendations.
    """
    
    prompt = f"""
    Create a medical meal plan for a user with the following requirements:
    
    Medical Condition: {request.condition}
    Severity: {request.severity}
    Dietary Restrictions: {', '.join(request.restrictions) if request.restrictions else 'None'}
    Nutritional Requirements: {request.requirements}
    Target Calories: {request.calories_per_day or 'Default for condition'}
    Additional Notes: {request.additional_notes or 'None'}
    
    Create a 7-day meal plan that is safe and appropriate for this medical condition.
    Ensure all meals follow medical dietary guidelines and consider the user's restrictions.
    """
    
    result = await Runner.run(
        medical_meal_planner_agent,
        input=prompt,
        context=ctx.context
    )
    
    medical_plan = result.final_output_as(MedicalMealPlan)
    ctx.context.meal_plan = medical_plan.days

    # Log medical meal plan creation
    medical_log_entry = f"medical_meal_plan_created_{request.condition}_{datetime.now().isoformat()}"
    ctx.context.handoff_logs.append(medical_log_entry)
    
    # Prepare response
    response = {
        "medical_meal_plan": medical_plan.model_dump(),
        "condition": request.condition,
        "severity": request.severity,
        "message": f"AI-generated medical meal plan created for {request.condition}. Please consult with your healthcare provider before starting this plan.",
        "safety_notes": [
            "This plan was generated by AI and is for general guidance only",
            "Always consult with your healthcare provider",
            "Monitor your condition and adjust as needed",
            "Keep track of any adverse reactions",
            "Follow your doctor's specific recommendations"
        ],
        "agent_used": True,
        "request_details": request.model_dump()
    }
    
    return response

