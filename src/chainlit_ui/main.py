from typing import Any, Dict, cast
from uuid import uuid4
import chainlit as cl
from chainlit.input_widget import TextInput

from src.context import UserSessionContext
from src.agent import HealthWellnessPlannerAgent


@cl.on_chat_start
async def on_chat_start():
   
    await cl.ChatSettings([
        TextInput(id="name", label="Name")
    ]).send()
   
    # Welcome message with app description
    welcome_name = "🌟 Welcome to Your Personal Health & Wellness Planner!"
    welcome_content = """
I'm here to help you achieve your fitness and wellness goals. Whether you want to:
• Set and track fitness goals
• Get personalized meal plans
• Create workout routines
• Monitor your progress
• Get nutrition advice

I'm your dedicated AI wellness coach ready to support your journey!
"""
    
    elements = [
        cl.Text(name=welcome_name, content=welcome_content)
    ]
    await cl.Message(content="", elements=elements).send()

    # Ask for user's name in a friendly way
    res = await cl.AskUserMessage(
        content="To get started, what's your name? This helps me personalize your experience! 😊"
    ).send()
    
    user_name = res.get("output", "Friend") if res else "Friend"    
    user = UserSessionContext(name=user_name, uid=str(uuid4()))
    agent = HealthWellnessPlannerAgent(user)
    msg = cl.Message(content="")
    
    result = agent.streaming(f"Hi! I am {user_name} (answer in max 50 tokens)")
    async for chunk in result.chunks():
        await msg.stream_token(chunk)
    
    await msg.update()
    cl.user_session.set("agent", agent)
    
    await cl.ChatSettings([
        TextInput(id="name", label="Name", initial=user_name)
    ]).send()
    


@cl.on_settings_update
async def on_settings_update(settings: Dict[str, Any]):
    
    agent = cast(HealthWellnessPlannerAgent, cl.user_session.get("agent"))
    agent.user.name = settings.get("name", "Friend")
    cl.user_session.set("agent", agent)
    


@cl.on_message
async def on_message(message: cl.Message):
    
    agent = cast(HealthWellnessPlannerAgent, cl.user_session.get("agent"))
    msg = cl.Message(content="")
    
    result = agent.streaming(message.content)
    async for chunk in result.chunks():
        await msg.stream_token(chunk)
    
    await msg.update()
    cl.user_session.set("agent", agent)

