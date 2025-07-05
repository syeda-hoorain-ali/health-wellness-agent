import asyncio
from agents import RunContextWrapper, function_tool
from typing import List, Optional

from src.context import Meal, MealDay, DietPreferences, UserSessionContext

# Example meal options for each diet
meal_options = {
    "vegetarian": [
        Meal(name="Oatmeal with Berries", type="breakfast", calories=350),
        Meal(name="Vegetable Stir Fry", type="lunch", calories=500),
        Meal(name="Chickpea Curry", type="dinner", calories=600),
        Meal(name="Greek Yogurt & Nuts", type="snacks", calories=350)
    ],
    "vegan": [
        Meal(name="Tofu Scramble", type="breakfast", calories=350),
        Meal(name="Quinoa Salad", type="lunch", calories=500),
        Meal(name="Lentil Stew", type="dinner", calories=600),
        Meal(name="Fruit & Seeds", type="snacks", calories=350)
    ],
    "pescatarian": [
        Meal(name="Avocado Toast", type="breakfast", calories=350),
        Meal(name="Tuna Salad", type="lunch", calories=500),
        Meal(name="Grilled Salmon", type="dinner", calories=600),
        Meal(name="Hummus & Veggies", type="snacks", calories=350)
    ],
    "keto": [
        Meal(name="Egg Muffins", type="breakfast", calories=350),
        Meal(name="Chicken Caesar Salad", type="lunch", calories=500),
        Meal(name="Beef Stir Fry", type="dinner", calories=600),
        Meal(name="Cheese & Olives", type="snacks", calories=350)
    ],
    "omnivore": [
        Meal(name="Scrambled Eggs", type="breakfast", calories=350),
        Meal(name="Turkey Sandwich", type="lunch", calories=500),
        Meal(name="Grilled Chicken", type="dinner", calories=600),
        Meal(name="Yogurt & Fruit", type="snacks", calories=350)
    ]
}


@function_tool(strict_mode=False)
async def meal_planner(
    ctx: RunContextWrapper[UserSessionContext],
    preferences: Optional[DietPreferences] = None,
) -> List[MealDay]:
   
    """
    Generates a weekly meal plan based on user preferences or session context.
    This function creates a list of `MealDay` objects, each representing a day's meal plan,
    tailored to the user's dietary preferences and daily calorie requirements. Preferences can
    be provided directly or inferred from the session context. The function adjusts meal
    calories proportionally to match the desired daily calorie intake.
    Args:
        ctx (RunContextWrapper[UserSessionContext]): The execution context containing user session data.
        preferences (Optional[Preferences]): User's dietary preferences and calorie goals. If not provided,
            preferences are taken from the session context.
    Returns:
        List[MealDay]: A list of 7 `MealDay` objects, each containing meals adjusted to the user's preferences.
    Raises:
        ValueError: If preferences are not provided and not available in the session context.
    """

    # Generate a simple meal plan based on preferences
    meal_plan: list[MealDay] = []
    if preferences is not None:
        prefs = preferences
    elif ctx.context.diet_preferences is not None:
        prefs = ctx.context.diet_preferences
    else:
        raise ValueError("Preferences must be provided either as a parameter or in the context.")

    diet = prefs.get("diet", "omnivore")
    calories_per_day = prefs.get("calories_per_day", 2000)

    # Just to make function async :)
    await asyncio.sleep(2)

    selected_meals = meal_options.get(diet, meal_options["omnivore"])

    # Adjust calories proportionally if needed
    total_meal_calories = sum(meal.calories for meal in selected_meals)
    calorie_ratio = calories_per_day / total_meal_calories if total_meal_calories else 1

    adjusted_meals = [
        Meal(
            name=meal.name,
            type=meal.type,
            calories=int(meal.calories * calorie_ratio)
        )
        for meal in selected_meals
    ]

    for i in range(1, 8):
        meal_plan.append(MealDay(day=i, meals=adjusted_meals))

    ctx.context.meal_plan = meal_plan
    ctx.context.diet_preferences = DietPreferences(diet=diet, calories_per_day=calories_per_day)
    return meal_plan
