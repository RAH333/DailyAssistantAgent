#import asyncio
from google.adk.agents.llm_agent import Agent
from google.adk.models.google_llm import Gemini
from google.adk.runners import InMemoryRunner, Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import google_search
from google.genai import types
import os

try:
    #GOOGLE_API_KEY = UserSecretsClient().get_secret("GOOGLE_API_KEY")
    GOOGLE_API_KEY = ""
    os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
    print(" Gemini API key setup complete.")
except Exception as e:
    print(
        f"🔑 Authentication Error: Please make sure you have added 'GOOGLE_API_KEY' to your Kaggle secrets. Details: {e}"
    )

# Define helper functions that will be reused throughout the notebook

from IPython.core import display
from IPython.core.display import HTML
from jupyter_server.serverapp import list_running_servers



retry_config=types.HttpRetryOptions(
    attempts=5,  # Maximum retry attempts
    exp_base=7,  # Delay multiplier
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504], # Retry on these HTTP errors
)

root_agent = Agent(
    model='gemini-2.5-flash-lite',
    name='root_agent',
    description='A helpful assistant for user questions.',
    instruction='Answer user questions to the best of your knowledge',
)

# Assistant Agent: Its job is to utilize various tools, agents, ADK, and models, such as the google_search tool, etc. Maintain and manage daily life data records, and process and present the records.
assistant_agent = Agent(
    name="AssistantAgent",
    model=Gemini(
        model="gemini-2.5-flash-lite",
        retry_options=retry_config
    ),
    instruction = """ You are a specialized assistant agent. Your only job is to utilize various tools, agents, ADK, and models, such as the google_search tool, etc. Maintain and manage daily life data records, and process and present the records.""",
    tools=[google_search,],
    output_key="assistant_record",  # The result of this agent will be stored in the session state with this key.
)



print("Gemini ASSISTANT agent setup complete.")
runner = InMemoryRunner(agent=root_agent)

print("Runner created.")
response =await runner.run_debug("What is Agent Development Kit from Google? What languages is the SDK available in?")

