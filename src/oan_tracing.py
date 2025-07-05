from agents import Agent, Runner, trace, set_default_openai_client, set_default_openai_api, set_tracing_disabled
from openai import AsyncOpenAI
from pydantic import BaseModel
from logfire import Logfire, configure
from typing import Dict, Any

configure()

external_client = AsyncOpenAI(
    api_key="AIzaSyD3rLFPuUhzZIm5uWQr-uHdGEJwAALl3ZI",
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

set_default_openai_client(client=external_client)
set_default_openai_api(api="chat_completions")
# set_tracing_disabled(disabled=)

class AgentLog(BaseModel):
    agent_name: str
    input: str
    output: str
    metadata: Dict[str, Any]
    processing_time: float
    tokens_used: int

async def main():
    # Initialize Logfire
    logfire = Logfire()
    
    # Create an agent
    agent = Agent(
        name="Code Generator",
        instructions="Generate Python code based on requirements.",
        model="gemini-2.0-flash"
    )

    # Create a trace for the code generation workflow
    with trace("Code Generation Workflow") as gen_trace:
        start_time = time.time()
        
        # Run the agent
        result = await Runner.run(
            agent,
            "Write a function to calculate factorial"
        )
        
        # Create structured log entry
        log_entry = AgentLog(
            agent_name=agent.name,
            input="Write a function to calculate factorial",
            output=result.final_output,
            metadata={
                "complexity": "medium",
                "language": "python",
                "model": agent.model
            },
            processing_time=time.time() - start_time,
            tokens_used=result.context_wrapper.usage.total_tokens
        )
        
        # Log the entry
        logfire.log("info", attributes=log_entry.model_dump(), msg_template="Test message")
        
        print(f"Generated code: {result.final_output}")

if __name__ == "__main__":
    import asyncio
    import time
    asyncio.run(main())
