# Health & Wellness Planner Agent

A sophisticated AI-powered health and wellness planning system built with OpenAI Agents SDK that provides personalized fitness and nutrition guidance through natural language conversation.

## 🌟 Features

### Core Capabilities
- **Natural Language Interaction**: Chat with the agent using everyday language
- **Goal Analysis**: Automatically extract and structure fitness goals from user input
- **Personalized Meal Planning**: Generate 7-day meal plans based on dietary preferences
- **Workout Recommendations**: Create customized workout plans based on fitness level and goals
- **Progress Tracking**: Monitor and log your health journey progress
- **Real-time Streaming**: Experience smooth, chatbot-like interactions with streaming responses

### Specialized Agent Handoffs
- **Nutrition Expert Agent**: Handles complex dietary needs (diabetes, allergies, etc.)
- **Injury Support Agent**: Provides injury-specific workout modifications
- **Escalation Agent**: Connects users to human coaches when needed

### Advanced Features
- **Input/Output Guardrails**: Ensures data validation and structured responses
- **Context Management**: Maintains conversation history and user preferences
- **Lifecycle Hooks**: Comprehensive logging and monitoring
- **State Persistence**: Remembers user goals and progress across sessions

## 🚀 Quick Start

### Prerequisites
- Python 3.12 or higher
- OpenAI API key

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd health-wellness-planner-agent
   ```

2. **Install dependencies**
   ```bash
   pip install -e .
   ```
   or using uv (recommended):
   ```bash
   uv sync
   ```

3. **Set up environment variables**
   Create a `.env` file in the project root:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   ```

4. **Run the application**
   ```bash
   python src/main.py
   ```

## 💬 Usage Examples

### Basic Interaction
```
User: I want to lose 5kg in 2 months
Agent: I'll help you create a plan to lose 5kg in 2 months. Let me analyze your goal...

User: I'm vegetarian
Agent: Perfect! I'll create a vegetarian meal plan for you. Here's your 7-day meal plan...
```

### Specialized Support
```
User: I have knee pain from running
Agent: I understand you're dealing with knee pain. Let me connect you with our injury support specialist...

User: I'm diabetic and need help with meal planning
Agent: I'll hand you over to our nutrition expert who specializes in diabetic meal planning...
```

## 🏗️ Project Structure

```
health-wellness-planner-agent/
├── src/
│   ├── main.py                 # Main application entry point
│   ├── agent.py               # Agent wrapper and streaming logic
│   ├── context.py             # Data models and user session context
│   ├── config.py              # Configuration settings
│   ├── hooks.py               # Lifecycle hooks for logging
│   ├── my_agents/             # Specialized agent implementations
│   │   ├── main_agent.py      # Primary health planner agent
│   │   ├── nutrition_expert_agent.py
│   │   ├── injury_support_agent.py
│   │   └── escalation_agent.py
│   ├── tools/                 # Agent tools for specific tasks
│   │   ├── goal_analyzer.py   # Goal extraction and validation
│   │   ├── meal_planner.py    # Meal plan generation
│   │   ├── workout_recommender.py
│   │   ├── tracker.py         # Progress tracking
│   │   ├── scheduler.py       # Check-in scheduling
│   │   └── escalator.py       # Handoff management
│   └── guardrails/            # Input/output validation
│       ├── health_guardrail.py
│       ├── nutrition_guardrail.py
│       ├── injury_guardrail.py
│       └── goal_analyzer_guardrail.py
├── pyproject.toml             # Project dependencies and metadata
└── README.md                  # This file
```

## 🔧 Technical Architecture

### Core Components

#### 1. **Main Agent** (`src/my_agents/main_agent.py`)
- Primary conversation handler
- Orchestrates tool usage and agent handoffs
- Manages user session context

#### 2. **Tools** (`src/tools/`)
- **GoalAnalyzerTool**: Extracts structured goals from natural language
- **MealPlannerTool**: Generates personalized meal plans
- **WorkoutRecommenderTool**: Creates fitness routines
- **ProgressTrackerTool**: Logs and tracks user progress
- **CheckinSchedulerTool**: Manages recurring check-ins

#### 3. **Context Management** (`src/context.py`)
- `UserSessionContext`: Central data model for user state
- Structured models for goals, meal plans, workout plans
- Progress tracking and handoff logging

#### 4. **Guardrails** (`src/guardrails/`)
- Input validation for user goals and preferences
- Output validation for tool responses
- Safety checks for health-related recommendations

### Data Models

#### Goal Structure
```python
class Goal(BaseModel):
    action: Literal["lose", "gain", "maintain"]
    quantity: float
    unit: Literal["kg", "lbs", "%"]
    duration: int
    timeframe_unit: Literal["days", "weeks", "months"]
```

#### Meal Planning
```python
class MealDay(BaseModel):
    day: int
    meals: List[Meal]  # Breakfast, lunch, dinner, snacks
```

#### Progress Tracking
```python
class ProgressUpdate(BaseModel):
    date: str
    weight: Optional[float]
    workouts_completed: Optional[int]
    meals_followed: Optional[int]
    notes: Optional[str]
    mood: Optional[str]
    sleep_hours: Optional[float]
    water_intake: Optional[float]
```

## 🔄 Agent Handoff Flow

The system intelligently routes users to specialized agents based on their needs:

1. **Main Agent** → **Nutrition Expert**: Complex dietary requirements
2. **Main Agent** → **Injury Support**: Physical limitations or injuries
3. **Main Agent** → **Escalation Agent**: Human coach requests

Each handoff preserves user context and conversation history.

## 🛡️ Safety & Validation

### Input Guardrails
- Goal format validation (quantity, metric, duration)
- Dietary preference validation
- Injury description validation

### Output Guardrails
- Structured JSON responses from tools
- Pydantic model validation
- Safety checks for health recommendations

## 📊 Monitoring & Logging

### Lifecycle Hooks
- Agent start/end events
- Tool invocation tracking
- Handoff logging
- User interaction metrics

### Progress Tracking
- Weight and fitness metrics
- Meal adherence
- Workout completion
- Mood and energy levels

## 🚀 Development

### Adding New Tools
1. Create tool in `src/tools/`
2. Implement async `run()` method
3. Add to agent tool list
4. Update guardrails if needed

### Adding New Agents
1. Create agent in `src/my_agents/`
2. Define handoff conditions
3. Add to main agent handoffs list
4. Implement `on_handoff()` if needed

### Running Tests
```bash
# Add test commands here when implemented
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

[Add your license information here]

## 🆘 Support

For issues and questions:
- Create an issue in the repository
- Check the documentation
- Review the assignment requirements in `ASSIGNMENT.md`

## 🔮 Future Enhancements

- [ ] Integration with fitness trackers
- [ ] Calendar integration for meal/workout scheduling
- [ ] Social features for accountability
- [ ] Mobile app interface
- [ ] Advanced analytics dashboard
- [ ] Integration with health professionals

---

**Built with ❤️ using OpenAI Agents SDK** 