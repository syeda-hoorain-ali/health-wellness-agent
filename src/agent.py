

from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Callable, List
from agents import RawResponsesStreamEvent, Runner, TResponseInputItem
from openai.types.responses import ResponseTextDeltaEvent

from src.context import UserSessionContext
from src.hooks import HealthWellnessHooks
from src.my_agents.main_agent import main_agent
import src.config


@dataclass
class Stream:
    chunks: Callable[[], AsyncIterator[str]] # Callable[[param1_type, param2_type], output_type]
    final_output: str   

class HealthWellnessPlannerAgent:
    
    def __init__(self, user: UserSessionContext):
        self.agent = main_agent
        self.user = user
        self.history: List[TResponseInputItem] = []
        self.hooks = HealthWellnessHooks()
 
    
    async def chat(self, prompt: str):
        
        new_history = self.history + [{"role": "user", "content": prompt}]
        result = await Runner.run(
            starting_agent=self.agent,
            input=new_history,
            context=self.user,
            hooks=self.hooks,
        )
        
        self.history += result.to_input_list()
        return result.final_output


    def streaming(self, prompt: str):

        new_history = self.history + [{"role": "user", "content": prompt}]
        result = Runner.run_streamed(
            starting_agent=self.agent,
            input=new_history,
            context=self.user,
            hooks=self.hooks,
        )
        
        async def chunks() -> AsyncIterator[str]:
            async for event in result.stream_events():
                if isinstance(event, RawResponsesStreamEvent) and isinstance(event.data, ResponseTextDeltaEvent):
                    chunk = event.data.delta
                    yield chunk
        
        self.history += result.to_input_list()
        return Stream(chunks=chunks, final_output=result.final_output)







