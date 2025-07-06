from collections.abc import AsyncIterator
from dataclasses import dataclass
import time
from typing import Callable, List

from agents import InputGuardrailTripwireTriggered, OutputGuardrailTripwireTriggered, RawResponsesStreamEvent, Runner, TResponseInputItem
from openai.types.responses import ResponseTextDeltaEvent

from src.context import UserSessionContext
from src.hooks import HealthWellnessHooks
from src.my_agents.main_agent import main_agent
from src.guardrails.guardrail_exceptions import handle_guardrail_exception
import src.config


@dataclass
class Stream:
    chunks: Callable[[], AsyncIterator[str]] # Callable[[param1_type, param2_type], output_type]
    """Callable that returns an async iterator yielding string chunks from the stream."""
    
    final_output: str
    """The complete final output string from the stream. This is None until the agent has finished running."""

class HealthWellnessPlannerAgent:
    """Agent for health and wellness planning with streaming capabilities and guardrail protection."""

    def __init__(self, user: UserSessionContext):
        self.agent = main_agent
        self.user = user
        self.history: List[TResponseInputItem] = []
        self.hooks = HealthWellnessHooks()
 
    
    async def chat(self, prompt: str) -> str:
        """Process a chat message and return the agent's response."""

        new_history = self.history + [{"role": "user", "content": prompt}]
        try:
            result = await Runner.run(
                starting_agent=self.agent,
                input=new_history,
                context=self.user,
                hooks=self.hooks,
            )
            
            self.history += result.to_input_list()
            return result.final_output

        except (InputGuardrailTripwireTriggered, OutputGuardrailTripwireTriggered) as e:
            agent_name = e.run_data.last_agent.name if e.run_data else self.agent.name
            
            return handle_guardrail_exception(
                exception=e,
                user_input=prompt,
                agent_name=agent_name,
                session_id=self.hooks.session_id,
                session_duration=round(time.time() - self.hooks.session_start_time, 2),
                user_name=self.user.name,
                user_uid=self.user.uid
            )


    def streaming(self, prompt: str) -> Stream:
        """Process a chat message and return a streaming response with chunks."""

        new_history = self.history + [{"role": "user", "content": prompt}]
        
        result = Runner.run_streamed(
            starting_agent=self.agent,
            input=new_history,
            context=self.user,
            hooks=self.hooks,
        )
        
        async def chunks() -> AsyncIterator[str]:
            try:
                async for event in result.stream_events():
                    if isinstance(event, RawResponsesStreamEvent) and isinstance(event.data, ResponseTextDeltaEvent):
                        chunk = event.data.delta
                        yield chunk
                        
            except (InputGuardrailTripwireTriggered, OutputGuardrailTripwireTriggered) as e:
                # Handle guardrail exceptions that occur during streaming
                agent_name = e.run_data.last_agent.name if e.run_data else self.agent.name
                
                response_message = handle_guardrail_exception(
                    exception=e,
                    user_input=prompt,
                    agent_name=agent_name,
                    session_id=self.hooks.session_id,
                    session_duration=round(time.time() - self.hooks.session_start_time, 2),
                    user_name=self.user.name,
                    user_uid=self.user.uid
                )
                
                # Yield the error message as chunks
                for word in response_message.split(' '):
                    yield word + ' '
        
        self.history += result.to_input_list()
        return Stream(chunks=chunks, final_output=result.final_output)

