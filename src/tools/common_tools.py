from typing import Any, Dict, Literal
from agents import RunContextWrapper, function_tool
from src.context import UserSessionContext



@function_tool(strict_mode=False)
async def read_context_data(
    ctx: RunContextWrapper[UserSessionContext],
    data_type: Literal["name", "goal", "workout_plan", "meal_plan", "diet_preferences", "injury_notes", "progress_logs", "handoff_logs", "all"]
) -> Dict[str, Any]:
    """
    Read specific data from the user's session context.
    
    This tool allows agents to access existing user data from the session context
    to provide better recommendations and personalized responses.
    
    Args:
        data_type: Type of data to retrieve from UserSessionContext:
            - "name": Name of the user
            - "goal": User's fitness goal
            - "workout_plan": Current workout plan
            - "meal_plan": Current meal plan
            - "diet_preferences": User's dietary preferences
            - "injury_notes": Any injury information
            - "progress_logs": User's progress history
            - "handoff_logs": History of agent handoffs
            - "all": All available context data
    
    Returns:
        Dict containing the requested context data
    """
    
    if data_type == "name":
        return {
            "name": ctx.context.name,
            "message": "Retrieved user's name"
        }
    
    if data_type == "goal":
        return {
            "goal": ctx.context.goal.model_dump() if ctx.context.goal else None,
            "message": "Retrieved user's fitness goal"
        }
    
    elif data_type == "workout_plan":
        return {
            "workout_plan": ctx.context.workout_plan.model_dump() if ctx.context.workout_plan else None,
            "message": "Retrieved current workout plan"
        }
    
    elif data_type == "meal_plan":
        return {
            "meal_plan": [day.model_dump() for day in ctx.context.meal_plan] if ctx.context.meal_plan else None,
            "message": "Retrieved current meal plan"
        }
    
    elif data_type == "diet_preferences":
        return {
            "diet_preferences": ctx.context.diet_preferences,
            "message": "Retrieved user's dietary preferences"
        }
    
    elif data_type == "injury_notes":
        return {
            "injury_notes": ctx.context.injury_notes,
            "message": "Retrieved injury information"
        }
    
    elif data_type == "progress_logs":
        return {
            "progress_logs": [log.model_dump() for log in ctx.context.progress_logs],
            "message": f"Retrieved {len(ctx.context.progress_logs)} progress log entries"
        }
    
    elif data_type == "handoff_logs":
        return {
            "handoff_logs": ctx.context.handoff_logs,
            "message": f"Retrieved {len(ctx.context.handoff_logs)} handoff log entries"
        }
    
    elif data_type == "all":
        return {
            "name": ctx.context.name,
            "goal": ctx.context.goal.model_dump() if ctx.context.goal else None,
            "workout_plan": ctx.context.workout_plan.model_dump() if ctx.context.workout_plan else None,
            "meal_plan": [day.model_dump() for day in ctx.context.meal_plan] if ctx.context.meal_plan else None,
            "diet_preferences": ctx.context.diet_preferences,
            "injury_notes": ctx.context.injury_notes,
            "progress_logs": [log.model_dump() for log in ctx.context.progress_logs],
            "handoff_logs": ctx.context.handoff_logs,
            "message": "Retrieved all available context data"
        } 