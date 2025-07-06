import os
from agents import set_default_openai_client, set_default_openai_api, set_tracing_disabled
from dotenv import find_dotenv, load_dotenv
import logfire
from openai import AsyncOpenAI

load_dotenv(find_dotenv())

LOGFIRE_TOKEN = os.getenv("LOGFIRE_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
MODEL = "gemini-2.0-flash"

if GEMINI_API_KEY is None:
    raise RuntimeError("Environment variable 'GEMINI_API_KEY' is not set.") 

if LOGFIRE_TOKEN is None:
    raise RuntimeError("Environment variable 'LOGFIRE_TOKEN' is not set.") 


external_client = AsyncOpenAI(api_key=GEMINI_API_KEY, base_url=BASE_URL)

set_default_openai_client(client=external_client)
set_default_openai_api(api="chat_completions")
set_tracing_disabled(disabled=True)

logfire.configure(token=LOGFIRE_TOKEN)
logfire.instrument_openai_agents()

