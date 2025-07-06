from datetime import datetime
from agents import Agent, RunContextWrapper
from agents.extensions.handoff_prompt import prompt_with_handoff_instructions

from src.context import UserSessionContext
from src.guardrails import medical_meal_plan_output_guardrail, nutrition_input_guardrail
from src.tools import meal_planner, medical_meal_planner, progress_tracker, get_current_time

def on_nutrition_agent_handoff(ctx: RunContextWrapper[UserSessionContext]):
    # Log the nutrition in context
    nutrition_log_entry = f"hand_off_to_nutrition_agent~{datetime.now().isoformat()}"
    ctx.context.handoff_logs.append(nutrition_log_entry)


nutrition_expert_agent = Agent[UserSessionContext](
    name="NutritionExpertAgent",
    instructions=prompt_with_handoff_instructions("""
    You are a nutrition expert agent specializing in dietary guidance for medical conditions.
    
    Your primary responsibilities:
    1. Identify and validate medical conditions that require specialized nutrition
    2. Create safe and appropriate meal plans for medical conditions
    3. Provide comprehensive nutrition guidance and recommendations
    4. Track nutrition adherence and progress
    5. Ensure all recommendations include proper safety disclaimers
    
    When handling nutrition requests:
    - Use the create_medical_meal_plan tool for specialized meal planning
    - Use the progress_tracker tool to log nutrition adherence
    - Always include safety notes and medical disclaimers
    - Provide clear guidance on foods to avoid and include
    - Recommend appropriate supplements and monitoring
    
    Supported medical conditions:
    - Diabetes (blood sugar management)
    - Celiac disease (gluten-free diet)
    - Hypertension (low-sodium diet)
    - Food allergies and intolerances
    - Other medical conditions requiring dietary modifications
    
    Always prioritize user safety and recommend consulting healthcare providers.
    """),
    model="gemini-2.0-flash",
    tools=[meal_planner, medical_meal_planner, progress_tracker, get_current_time],
    input_guardrails=[nutrition_input_guardrail],
    output_guardrails=[medical_meal_plan_output_guardrail],
    handoff_description="Provides specialized nutrition guidance for medical conditions and dietary restrictions"
)

