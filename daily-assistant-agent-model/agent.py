import asyncio
from google.adk.agents.llm_agent import Agent
from google.adk.models.google_llm import Gemini
from google.adk.runners import InMemoryRunner, Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import google_search
from google.genai import types
import os
import dailyassistantagent 
import agents
try:
    #GOOGLE_API_KEY = UserSecretsClient().get_secret("GOOGLE_API_KEY")
    GOOGLE_API_KEY = "AIzaSyDqdbj_GYRJKbeLSecmoIeagwFrv2ZdB8w"
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


# Gets the proxied URL in the Kaggle Notebooks environment
def get_adk_proxy_url():
    PROXY_HOST = "https://127.0.0.1"
    ADK_PORT = "8888"
    #PROXY_HOST = "https://kkb-production.jupyter-proxy.kaggle.net"
    #ADK_PORT = "8000"
    servers = list(list_running_servers())
    #servers = list("https://127.0.0.1")
    if not servers:
        raise Exception("No running Jupyter servers found.")

    baseURL = servers[0]["base_url"]

    try:
        path_parts = baseURL.split("/")
        kernel = path_parts[2]
        token = path_parts[3]
    except IndexError:
        raise Exception(f"Could not parse kernel/token from base URL: {baseURL}")

    url_prefix = f"/k/{kernel}/{token}/proxy/proxy/{ADK_PORT}"
    url = f"{PROXY_HOST}{url_prefix}"

    styled_html = f"""
    <div style="padding: 15px; border: 2px solid #f0ad4e; border-radius: 8px; background-color: #fef9f0; margin: 20px 0;">
        <div style="font-family: sans-serif; margin-bottom: 12px; color: #333; font-size: 1.1em;">
            <strong>⚠️ IMPORTANT: Action Required</strong>
        </div>
        <div style="font-family: sans-serif; margin-bottom: 15px; color: #333; line-height: 1.5;">
            The ADK web UI is <strong>not running yet</strong>. You must start it in the next cell.
            <ol style="margin-top: 10px; padding-left: 20px;">
                <li style="margin-bottom: 5px;"><strong>Run the next cell</strong> (the one with <code>!adk web ...</code>) to start the ADK web UI.</li>
                <li style="margin-bottom: 5px;">Wait for that cell to show it is "Running" (it will not "complete").</li>
                <li>Once it's running, <strong>return to this button</strong> and click it to open the UI.</li>
            </ol>
            <em style="font-size: 0.9em; color: #555;">(If you click the button before running the next cell, you will get a 500 error.)</em>
        </div>
        <a href='{url}' target='_blank' style="
            display: inline-block; background-color: #1a73e8; color: white; padding: 10px 20px;
            text-decoration: none; border-radius: 25px; font-family: sans-serif; font-weight: 500;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2); transition: all 0.2s ease;">
            Open ADK Web UI (after running cell below) ↗
        </a>
    </div>
    """

    display(HTML(styled_html))

    return url_prefix

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




