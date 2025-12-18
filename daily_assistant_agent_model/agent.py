import asyncio
from google.adk.agents.llm_agent import Agent
from google.adk.models.google_llm import Gemini
from google.adk.runners import InMemoryRunner, Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import google_search
from google.genai import types
import os
from .agents import dailyassistantagent 
from .agents import agents

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



print("Gemini Assitant agent setup complete.")
runner = InMemoryRunner(agent=root_agent)

print("Runner created.")
prompt=""
import asyncio
#from import agent # Assuming 'agent' has an awaitable 'runner.run_debug(prompt)'

async def main_task(): # Wrap the main logic in an async function
    #response = await agent.runner.run_debug(prompt) # Now 'await' is inside an async function
    # You can process the response here
    while True:
        prompt=input("Please, Enter your input here.")
        response = await runner.run_debug(prompt)
#response = await runner.run_debug("What is the Agent Development Kit from Google? What languages is the SDK available in?")
#response = await runner.run_debug("What's the weather in india?")

####url_prefix = get_adk_proxy_url()

if __name__ == "__main__":
    asyncio.run(main_task()) # Run the async function using the asyncio event loop
    


#adk web --url_prefix {url_prefix}









