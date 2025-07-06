from agents import Agent, RunContextWrapper, handoff
from agents.extensions.handoff_prompt import prompt_with_handoff_instructions

from src.context import UserSessionContext
from src.guardrails import health_input_guardrail
from src.tools import (
    add_injury_note,
    escalate_to_human_coach,
    goal_analyzer,
    meal_planner,
    read_context_data,
    checkin_scheduler_google,
    checkin_scheduler_local,
    progress_tracker,
    workout_recommender,
    get_current_time
)
from src.my_agents import (
    escalation_agent,
    on_escalation_agent_handoff,
    injury_support_agent,
    on_injury_support_agent_handoff,
    nutrition_expert_agent,
    on_nutrition_agent_handoff,
)


def dynamic_instructions(
    context: RunContextWrapper[UserSessionContext], 
    agent: Agent[UserSessionContext]
) -> str:
    # Get user context information
    user_name = context.context.name
    has_goal = context.context.goal is not None
    has_meal_plan = context.context.meal_plan is not None
    has_workout_plan = context.context.workout_plan is not None
    has_injury_notes = context.context.injury_notes is not None
    has_diet_preferences = context.context.diet_preferences is not None
    progress_count = len(context.context.progress_logs)
    
    # Build personalized context summary
    context_summary = f"User: {user_name}\n"
    
    if has_goal:
        goal = context.context.goal
        context_summary += f"Current Goal: {goal.action} {goal.quantity} {goal.unit} in {goal.duration} {goal.timeframe_unit}\n"
    
    if has_diet_preferences:
        diet = context.context.diet_preferences
        context_summary += f"Dietary Preferences: {diet.get('diet', 'Not specified')}, {diet.get('calories_per_day', 'Not specified')} calories/day\n"
    
    if has_injury_notes:
        context_summary += f"Injury Information: {context.context.injury_notes[-3:]}...\n"
    
    if has_meal_plan:
        context_summary += f"Meal Plan: {len(context.context.meal_plan)} days available\n"
    
    if has_workout_plan:
        context_summary += f"Workout Plan: Available\n"
    
    if progress_count > 0:
        context_summary += f"Progress Tracking: {progress_count} entries logged\n"
    
    # Build dynamic instructions based on context
    base_instructions = f"""
    You are a comprehensive Health & Wellness Planner Agent that helps users achieve their fitness and health goals.
    
    Current User Context:
    {context_summary}
    
    Your primary responsibilities:
    1. Understand and analyze user fitness goals using natural language processing
    2. Generate personalized meal plans based on dietary preferences and restrictions
    3. Create workout recommendations tailored to user experience and goals
    4. Schedule progress check-ins and track user progress over time
    5. Provide real-time, streaming responses for an engaging user experience
    6. Handoff to specialized agents when specific expertise is needed
    """
    
    # Add context-specific guidance
    if not has_goal:
        base_instructions += "\n7. Help users set clear, achievable fitness goals if they haven't set one yet"
    
    if has_goal and not has_workout_plan:
        base_instructions += "\n7. Recommend a workout plan that aligns with their current goal"
    
    if has_goal and not has_meal_plan:
        base_instructions += "\n7. Suggest a meal plan that supports their fitness goal"
    
    if has_injury_notes:
        base_instructions += "\n7. Consider their injury limitations when making recommendations"
    
    if progress_count > 0:
        base_instructions += "\n7. Reference their progress history to provide continuity and motivation"
    
    base_instructions += f"""
    
    Available Tools:
    - goal_analyzer: Parse and structure fitness goals from natural language
    - meal_planner: Generate personalized meal plans
    - workout_recommender: Create tailored workout schedules
    - progress_tracker: Log and track user progress updates
    - checkin_scheduler_local: Schedule local calendar reminders
    - checkin_scheduler_google: Schedule Google Calendar reminders
    - read_context_data: Access user session information
    - add_injury_note: Record injury information for adaptations
    - get_current_time: Get current date/time information for scheduling
    
    Handoff Triggers:
    - When users want to speak with a human coach → EscalationAgent
    - When users mention injuries or physical limitations → InjurySupportAgent
    - When users have complex dietary needs (diabetes, allergies) → NutritionExpertAgent
    
    Always be supportive, encouraging, and prioritize user safety. Use streaming responses
    to maintain engagement and provide real-time feedback.
    
    Time and Scheduling Guidelines:
    - ALWAYS use the get_current_time tool when you need current date/time information
    - Never ask users for basic date/time information like current year, month, or day
    - Use current time information for scheduling appointments, check-ins, and planning
    - When scheduling recurring events, use the current date as the starting point if not specified
    - For scheduling tools, you can omit the start_date parameter to use current date automatically
    - When users say "schedule for tomorrow", "weekly on Thursday", or "monthly on the 5th", 
      use current time to calculate the appropriate start date
    
    Personalization Guidelines:
    - Use the user's name ({user_name}) in responses when appropriate
    - Reference their existing goals, plans, and progress when relevant
    - Build upon previous conversations and recommendations
    - Provide continuity in your advice based on their history
    """
    
    return prompt_with_handoff_instructions(base_instructions)




main_agent = Agent[UserSessionContext](
    name="Health Wellness Planner Agent",
    instructions=dynamic_instructions,
    model="gemini-2.0-flash",
    tools=[
        goal_analyzer,
        meal_planner,
        workout_recommender,
        progress_tracker,
        checkin_scheduler_local,
        checkin_scheduler_google,
        read_context_data,
        add_injury_note,
        escalate_to_human_coach,
        get_current_time,
    ],
    input_guardrails=[health_input_guardrail],
    handoffs=[
        handoff(escalation_agent, on_handoff=on_escalation_agent_handoff),
        handoff(injury_support_agent, on_handoff=on_injury_support_agent_handoff),
        handoff(nutrition_expert_agent, on_handoff=on_nutrition_agent_handoff),
    ]
)

