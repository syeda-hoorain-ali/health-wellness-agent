Below is a breakdown of every component in your Health & Wellness Planner assignment, organized by Tools, Agents, and Guardrails. For each item I describe:

1. **Purpose**
2. **Behavior (what it does)**
3. **Inputs (parameters)**
4. **Outputs (what it returns)**

---

## 🔧 Tools

| Tool Name                  | Purpose                                                                               |
| -------------------------- | ------------------------------------------------------------------------------------- |
| **GoalAnalyzerTool**       | Parse and structure a free-form “fitness goal” sentence into a validated JSON schema. |
| **MealPlannerTool**        | Asynchronously generate a multi-day meal plan matching dietary constraints.           |
| **WorkoutRecommenderTool** | Create a workout schedule tailored to user experience, goals, and any limitations.    |
| **CheckinSchedulerTool**   | Schedule recurring calendar reminders (e.g. weekly check-ins) for progress tracking.  |
| **ProgressTrackerTool**    | Log user updates (e.g. actual weight, workouts completed) and update session context. |

### 1. GoalAnalyzerTool

* **What it does:**

  * Accepts a user’s natural-language goal (e.g. “lose 5 kg in 2 months”)
  * Validates format (quantity + unit + timeframe)
  * Maps into a Pydantic model:

    ```python
    class Goal(BaseModel):
      action: Literal["lose","gain","maintain"]
      quantity: float
      unit: Literal["kg","lbs","%"]
      duration: int  # days or weeks
      timeframe_unit: Literal["days","weeks","months"]
    ```
* **Parameters:**

  * `raw_text: str` (the user’s goal sentence)
  * `context: RunContextWrapper[UserSessionContext]` (to store result)
* **Returns:**

  * `Goal` model instance (or raises validation errors via output guardrail)

### 2. MealPlannerTool

* **What it does:**

  * Based on `diet_preferences` (e.g. “vegetarian”, “diabetic”), streams back a 7-day meal plan
  * Each day: breakfast/lunch/dinner/snacks, calorie estimates
* **Parameters:**

  * `preferences: dict` (e.g. `{ "diet": "vegetarian", "calories_per_day": 1800 }`)
  * `context: RunContextWrapper[...]`
* **Returns:**

  * `List[MealDay]` where `MealDay` is a Pydantic model with day index and meal list

### 3. WorkoutRecommenderTool

* **What it does:**

  * Reads parsed goals + experience level + any injury notes
  * Produces a weekly workout plan: days, exercises, sets × reps or duration
* **Parameters:**

  * `goals: Goal` (from GoalAnalyzer)
  * `experience: Literal["beginner","intermediate","advanced"]`
  * `injury_notes: Optional[str]`
  * `context`
* **Returns:**

  * `WorkoutPlan` Pydantic model (dict with days→exercises)

### 4. CheckinSchedulerTool

* **What it does:**

  * Creates calendar reminders (via iCal or other scheduler) at specified intervals
  * Returns a confirmation or link for the scheduled event
* **Parameters:**

  * `user_id: int`, `frequency: Literal["daily","weekly","monthly"]`
  * `start_date: date`
  * `context`
* **Returns:**

  * `ScheduleConfirmation` model (with event IDs, next occurrence)

### 5. ProgressTrackerTool

* **What it does:**

  * Appends user-reported progress (e.g. weight, completed workouts) into `context.progress_logs`
  * Optionally recalculates progress metrics
* **Parameters:**

  * `update: Dict[str,Any]` (e.g. `{"date":"2025-07-03","weight":74.2}`)
  * `context`
* **Returns:**

  * Updated `UserSessionContext` (with new `progress_logs` entry)

---

## 🤝 Specialized Agents

| Agent Name               | Trigger Condition                                |
| ------------------------ | ------------------------------------------------ |
| **EscalationAgent**      | “I want to talk to a human coach”                |
| **NutritionExpertAgent** | Complex dietary needs (e.g. diabetes, allergies) |
| **InjurySupportAgent**   | Mentions injuries or physical limitations        |

### 1. EscalationAgent

* **Purpose:**

  * Handoff to a human coach or call center
  * Log the request and provide next steps/contact info
* **Behavior:**

  1. `on_handoff()`: append `"escalated_to_human"` to `context.handoff_logs`
  2. Message user with “Connecting you to a live coach…”
* **Tools Available:**

  * None (handing off ends the tool loop)
* **Guardrails:**

  * **Input:** Only accept explicit “speak to human” intents
  * **Output:** Always return a standard JSON `{ "status": "escalated", "contact": "coach@example.com" }`

### 2. NutritionExpertAgent

* **Purpose:**

  * Provide deep dietary guidance for special conditions
* **Behavior:**

  1. Validate specific constraints (via guardrails)
  2. Use `MealPlannerTool` with stricter parameters (e.g. sugar < 30 g/day)
  3. Stream suggestions meal by meal
* **Tools Available:**

  * `MealPlannerTool`
  * `ProgressTrackerTool` (to log nutrition adherence)
* **Guardrails:**

  * **Input:** Must include a medical condition field (`"diabetic": true`)
  * **Output:** Must output a `MedicalMealPlan` Pydantic model

### 3. InjurySupportAgent

* **Purpose:**

  * Adapt workouts around injuries
* **Behavior:**

  1. Parse `injury_notes`
  2. Call `WorkoutRecommenderTool` with blocked exercises
  3. Provide “safe alternatives” list
* **Tools Available:**

  * `WorkoutRecommenderTool`
  * `ProgressTrackerTool`
* **Guardrails:**

  * **Input:** Injury type + severity required
  * **Output:** Must return JSON with fields `{ allowed_exercises, prohibited_exercises }`

---

## 🔒 Guardrails

### Input Guardrails

Enforce that user inputs are well-formed before tools run.

| Guardrail Name           | Purpose                                                                 |
| ------------------------ | ----------------------------------------------------------------------- |
| **ValidateGoalFormat**   | Ensure goals have quantity + unit + duration before `GoalAnalyzerTool`. |
| **ValidateDietaryInput** | Block unsupported diet terms; require known preferences.                |
| **ValidateInjuryInput**  | Require injury description + severity level.                            |

* **What each does:**

  * Parses raw string; applies regex or Pydantic checks; raises user-friendly errors if invalid.
* **What they return:**

  * On success: normalized dict or Pydantic model.
  * On failure: a validation error message (halts agent until corrected).

### Output Guardrails

Ensure tool outputs match expected schemas.

| Guardrail Name               | Purpose                                                        |
| ---------------------------- | -------------------------------------------------------------- |
| **EnsureJSONStructure**      | Wrap tool returns in strict JSON/Pydantic models.              |
| **ValidateMealPlanModel**    | Confirm `MealPlannerTool` output conforms to `List[MealDay]`.  |
| **ValidateWorkoutPlanModel** | Confirm `WorkoutRecommenderTool` returns `WorkoutPlan` schema. |

* **What each does:**

  * Takes the raw return value of a tool call; validates it against a Pydantic schema.
  * If validation fails, raises an exception that the agent can catch and retry or report.
* **What they return:**

  * The validated model instance (e.g. a Python object with typed fields).

---

### How Guardrails and Agents Interact

* **Agents** include references to the specific guardrails they require.

  ```python
  main_agent = Agent(
    tools=[GoalAnalyzerTool, MealPlannerTool, …],
    input_guardrails=[ValidateGoalFormat, ValidateDietaryInput],
    output_guardrails=[EnsureJSONStructure, ValidateMealPlanModel],
    handoffs=[NutritionExpertAgent, InjurySupportAgent, EscalationAgent],
    …
  )
  ```
* Before calling a tool, the **Input Guardrails** run to normalize/validate user input.
* After each tool call, the **Output Guardrails** run to ensure structured, trustworthy returns.
* **Handoff** logic in the main agent routes control to one of the specialized agents when their trigger conditions are met.

---

This structure ensures:

* **Tools** encapsulate discrete functionality (analysis, planning, scheduling, tracking).
* **Agents** orchestrate conversation flow, tool usage, and handoffs based on user needs.
* **Guardrails** maintain input hygiene and output integrity, preventing malformed data from creeping into the system.
