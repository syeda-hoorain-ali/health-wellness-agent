from typing import Literal
from agents import Agent, RunContextWrapper, Runner, function_tool

from src.context import UserSessionContext, WorkoutPlan


workout_recommender_agent = Agent(
    name="Workout Recommender",
    instructions=(
        "You are a fitness expert specializing in creating personalized workout plans. "
        "Use the user's fitness goal, diet preferences, injury notes, and experience level to generate a weekly workout plan. "
        "Ensure the plan is safe, effective, and tailored to the user's needs. "
        "Output the plan as a WorkoutPlan with a 'days' field containing a dictionary where:"
        "- Keys are day names (Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday)"
        "- Values are lists of exercise dictionaries with fields like 'exercise', 'sets', 'reps', 'duration', etc."
        "Example format: {'days': {'Monday': [{'exercise': 'Running', 'duration': '30 minutes', 'intensity': 'easy'}]}}"
    ),
    model="gemini-2.0-flash",
    output_type=WorkoutPlan,
)


@function_tool(strict_mode=False)
async def workout_recommender(
    ctx: RunContextWrapper[UserSessionContext],
    experience: Literal["beginner", "intermediate", "advance"],
) -> WorkoutPlan:

    """
    Generates a personalized weekly workout plan for a user based on their experience level, goals, dietary preferences, and injury notes.
    Args:
        experience (Literal["beginner", "intermediate", "advance"]): The user's workout experience level.
    Returns:
        WorkoutPlan: A structured workout plan mapping days of the week to lists of exercises, including sets and reps, tailored to the user's profile and restrictions.
    Raises:
        TypeError: If the final output cannot be converted to a WorkoutPlan.
    """

    user = ctx.context
    prompt = f"""
        Create a personalized weekly workout plan for the following user:  
        Name: {user.name}  
        Experience level: {experience}  
        Goal: {user.goal}  
        Diet preferences: {user.diet_preferences}  
        Injury notes: {user.injury_notes}  
        Please provide a workout plan as a dictionary mapping days of the week to a list of exercises, 
        including sets and reps for each exercise. Ensure the plan is safe and aligns with the user's goals and restrictions.
    """

    print("Workout recommender tool called")
    
    try:
        result = await Runner.run(
            workout_recommender_agent, 
            input=prompt,
            context=ctx.context
        )
        
        print("Agent run completed successfully")
        print(f"Raw result: {result}")
        
        workout_plan = result.final_output_as(WorkoutPlan)
        print(f"Generated workout plan: {workout_plan}")
        ctx.context.workout_plan = workout_plan
        
        print("Workout plan saved to context successfully")
        return workout_plan
        
    except Exception as e:
        print(f"ERROR in workout_recommender: {e}")
        print(f"Error type: {type(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        raise e


