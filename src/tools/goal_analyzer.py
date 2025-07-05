from agents import Agent

from src.context import Goal
from src.guardrails import goal_input_guardrail

goal_analyzer_agent = Agent(
    name="Goal Analyzer Agent",
    instructions=(
        "You are a goal analyzer agent. Your task is to take raw, unstructured goal input from the user "
        "and convert it into a structured Goal object. Carefully extract the quantity, metric, and duration "
        "from the user's input. Ensure all required fields are present, valid, and clearly explained in your output. "
        "If any information is missing or ambiguous, provide reasoning in your output."
    ),
    model="gemini-2.0-flash",
    output_type=Goal,
    input_guardrails=[goal_input_guardrail]
)


goal_analyzer = goal_analyzer_agent.as_tool(
    tool_name="goal_analyzer",
    tool_description="""
Analyzes and converts raw user goal input into a structured Goal object.

Args:
    raw_text (str): The raw goal description provided by the user.

Returns:
    Goal: A structured Goal object containing the parsed and validated goal details.
"""
)
