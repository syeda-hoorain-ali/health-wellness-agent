from pydantic import BaseModel
from typing import Optional, List, Dict, Any, Literal, TypedDict


# Goal model for structured fitness goals
class Goal(BaseModel):
    action: Literal["lose", "gain", "maintain"]
    quantity: float
    unit: Literal["kg", "lbs", "%"]
    duration: int
    timeframe_unit: Literal["days", "weeks", "months"]



# MealDay model for meal planning
class Meal(BaseModel):
    name: str
    calories: float 
    type: Literal["breakfast", "lunch", "dinner", "snacks"]

class MealDay(BaseModel):
    day: int
    meals: List[Meal]  # e.g., [{"type": "breakfast", "items": [...], "calories": ...}]

# MedicalMealPlan for special dietary needs
class MedicalMealPlan(BaseModel):
    days: List[MealDay]
    condition: str



# WorkoutPlan model for workout recommendations
class WorkoutPlan(BaseModel):
    days: Dict[str, List[Dict[str, Any]]]  # e.g., {"Monday": [{"exercise": ..., "sets": ..., "reps": ...}], ...}


# ScheduleConfirmation for check-in scheduling
class ScheduleConfirmation(BaseModel):
    event_id: str
    next_occurrence: str


class DietPreferences(TypedDict):
    diet: Literal["vegetarian", "vegan", "pescatarian", "keto", "omnivore"]
    calories_per_day: int


class InjuryNote(BaseModel):
    injury_description: str
    severity_level: str
    affected_body_parts: list[str]
    restrictions: list[str]
    notes: Optional[str] = None


# Progress update model for structured updates
class ProgressUpdate(BaseModel):
    date: str 
    # Date of the progress update in YYYY-MM-DD format
    weight: Optional[float] = None 
    # Current weight in kg or lbs
    workouts_completed: Optional[int] = None 
    # Number of workouts completed
    meals_followed: Optional[int] = None 
    # Number of meals followed from plan
    notes: Optional[str] = None 
    # Additional notes about progress
    mood: Optional[str] = None 
    # Mood or energy level
    sleep_hours: Optional[float] = None 
    # Hours of sleep
    water_intake: Optional[float] = None 
    # Water intake in liters



# User session context shared across all tools and agents
class UserSessionContext(BaseModel):
    name: str
    uid: str
    goal: Optional[Goal] = None
    diet_preferences: Optional[DietPreferences] = None
    workout_plan: Optional[WorkoutPlan] = None
    meal_plan: Optional[List[MealDay]] = None
    injury_notes: List[InjuryNote] = []
    handoff_logs: List[str] = []
    progress_logs: List[ProgressUpdate] = []

