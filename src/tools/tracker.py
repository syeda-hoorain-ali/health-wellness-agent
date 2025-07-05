from datetime import datetime
from typing import Dict, Any, Optional, List
from agents import RunContextWrapper, function_tool
from pydantic import BaseModel

from src.context import Goal, ProgressUpdate, UserSessionContext


# Progress summary model for tracking overall progress
class ProgressSummary(BaseModel):
    total_updates: int
    weight_change: Optional[float] = None
    workouts_completed_total: int
    meals_followed_total: int
    average_mood: Optional[str] = None
    average_sleep: Optional[float] = None
    progress_percentage: Optional[float] = None


@function_tool(strict_mode=False)
async def progress_tracker(
    ctx: RunContextWrapper[UserSessionContext],
    update_data: Optional[Dict[str, Any]] = None,
    raw_update: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Tracks user progress updates and maintains session context.
    
    This function accepts progress updates either as structured data or raw text,
    validates the input, stores it in the session context, and calculates
    progress metrics. It can handle various types of progress data including weight,
    workout completion, meal adherence, mood, sleep, and water intake.
    
    Args:
        update_data (Optional[Dict[str, Any]]): Structured progress update data. If provided, this takes precedence.
        raw_update (Optional[str]): Raw text description of progress update. Used if update_data is not provided.
    
    Returns:
        Dict[str, Any]: A dictionary containing the progress update, progress summary, confirmation message and total updates.
    
    Raises:
        ValueError: If neither update_data nor raw_update is provided.
    """
    
    if update_data is None and raw_update is None:
        raise ValueError("Either update_data or raw_update must be provided")
    
    # Process the update
    if update_data is not None:
        # Use structured data directly
        progress_update = ProgressUpdate(**update_data)
    else:
        # For raw text, create a note with current date
        progress_update = ProgressUpdate(
            date=datetime.now().strftime("%Y-%m-%d"),
            notes=raw_update
        )
    
    # Add timestamp if not present
    if not progress_update.date:
        progress_update.date = datetime.now().strftime("%Y-%m-%d")
    
    ctx.context.progress_logs.append(progress_update)
    
    # Calculate progress summary
    summary = calculate_progress_summary(ctx.context.progress_logs, ctx.context.goal)
    
    # Prepare response
    response = {
        "progress_update": progress_update,
        "progress_summary": summary.model_dump(),
        "message": f"Progress update recorded for {progress_update.date}. Keep up the great work!",
        "total_updates": len(ctx.context.progress_logs)
    }
    
    return response


def calculate_progress_summary(
    progress_logs: List[ProgressUpdate], 
    goal: Optional[Goal] = None
) -> ProgressSummary:
    """
    Calculate progress summary from accumulated progress logs.
    
    Args:
        progress_logs: List of progress update dictionaries
        goal: User's fitness goal (optional)
    
    Returns:
        ProgressSummary: Calculated progress metrics
    """
    
    if not progress_logs:
        return ProgressSummary(
            total_updates=0,
            workouts_completed_total=0,
            meals_followed_total=0
        )
    
    # Extract numeric values
    weights = [log.weight for log in progress_logs if log.weight is not None]
    workouts = [log.workouts_completed for log in progress_logs if log.workouts_completed is not None]
    meals = [log.meals_followed for log in progress_logs if log.meals_followed is not None]
    sleep_hours = [log.sleep_hours for log in progress_logs if log.sleep_hours is not None]

    
    # Calculate weight change
    weight_change = None
    if len(weights) >= 2:
        weight_change = weights[-1] - weights[0]
    
    # Calculate averages
    average_sleep = sum(sleep_hours) / len(sleep_hours) if sleep_hours else None
    
    # Calculate progress percentage based on goal
    progress_percentage = None
    if goal and weights:
        if goal.action == "lose" and weight_change:
            progress_percentage = min(100, max(0, (weight_change / goal.quantity) * 100))
        elif goal.action == "gain" and weight_change:
            progress_percentage = min(100, max(0, (weight_change / goal.quantity) * 100))
    
    return ProgressSummary(
        total_updates=len(progress_logs),
        weight_change=weight_change,
        workouts_completed_total=sum(workouts),
        meals_followed_total=sum(meals),
        average_sleep=average_sleep,
        progress_percentage=progress_percentage
    )

