from typing import TypedDict
from agents import Agent, Runner, function_tool
import logfire

from httpx import AsyncClient


logfire.configure()
logfire.instrument_openai_agents()

class Location(TypedDict):
    lat: float
    long: float


@function_tool(strict_mode=False)
async def fetch_weather(location: Location) -> str:
    """Fetch the weather for a given location.

    Args:
        location: The location to fetch the weather for.
    """
    
    return 'sunny'

agent = Agent(name='weather agent', tools=[fetch_weather])


async def main():
    async with AsyncClient() as client:
        logfire.instrument_httpx(client)
        result = await Runner.run(agent, 'Get the weather at lat=51 lng=0.2', context=client)
    print(result.final_output)


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())

