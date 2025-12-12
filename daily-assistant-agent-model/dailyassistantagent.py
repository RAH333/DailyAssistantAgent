# @title Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import asyncio
import logging
import os
import uuid

from kaggle_secrets import UserSecretsClient

#from google.adk.agents import Agent
#from google.adk.agents import LlmAgent
#from google.adk.agents import Agent, SequentialAgent, ParallelAgent, LoopAgent
from google.adk.agents import Agent, SequentialAgent, ParallelAgent, LoopAgent,LlmAgent

from google.adk.agents.base_agent import BaseAgent
from google.adk.agents.callback_context import CallbackContext

#from google.adk.apps.app import App, EventsCompactionConfig
#from google.adk.apps.app import App, ResumabilityConfig
from google.adk.apps.app import App, EventsCompactionConfig, ResumabilityConfig

from google.adk.code_executors import BuiltInCodeExecutor


from google.adk.models.google_llm import Gemini
from google.adk.models.llm_request import LlmRequest

from google.adk.memory import InMemoryMemoryService

from google.adk.plugins.base_plugin import BasePlugin
from google.adk.plugins.logging_plugin import (
    LoggingPlugin,
)  # <---- 1. Import the Plugin


#from google.adk.runners import InMemoryRunner
#from google.adk.runners import Runner
from google.adk.runners import InMemoryRunner, Runner


#from google.adk.sessions import InMemorySessionService
#from google.adk.sessions import DatabaseSessionService
from google.adk.sessions import DatabaseSessionService, InMemorySessionService

#from google.adk.tools import google_search
#from google.adk.tools import AgentTool, FunctionTool, google_search
#from google.adk.tools import google_search, AgentTool, ToolContext
#from google.adk.tools import load_memory, preload_memory

from google.adk.tools import AgentTool, FunctionTool, google_search, load_memory, preload_memory, ToolContext 
from google.adk.tools.function_tool import FunctionTool
from google.adk.tools.google_search_tool import google_search

from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from google.adk.tools.tool_context import ToolContext

from google.genai import types

from mcp import StdioServerParameters
#from typing import Any, Dict
#from typing import List
from typing import Any, Dict, List


print("✅ ADK components imported successfully.")

# Clean up any previous logs
for log_file in ["logger.log", "web.log", "tunnel.log"]:
    if os.path.exists(log_file):
        os.remove(log_file)
        print(f"🧹 Cleaned up {log_file}")

# Configure logging with DEBUG log level.
logging.basicConfig(
    filename="logger.log",
    level=logging.DEBUG,
    format="%(filename)s:%(lineno)s %(levelname)s:%(message)s",
)

print("✅ Logging configured")

try:
    GOOGLE_API_KEY = UserSecretsClient().get_secret("GOOGLE_API_KEY")
    os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
    print("✅ Gemini API key setup complete.")
except Exception as e:
    print(
        f"🔑 Authentication Error: Please make sure you have added 'GOOGLE_API_KEY' to your Kaggle secrets. Details: {e}"
    )

retry_config=types.HttpRetryOptions(
    attempts=5,  # Maximum retry attempts
    exp_base=7,  # Delay multiplier
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504], # Retry on these HTTP errors
)
from google.adk.agents.llm_agent import Agent

root_agent = Agent(
    model='gemini-2.5-flash-lite',
    name='root_agent',
    description='A helpful assistant for user questions.',
    instruction='Answer user questions to the best of your knowledge',
)
print(f'Hi, I am your Daily life Assistant.')

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


# Daily Assistant Agent: Its job is to utilize various tools, agents, ADK, and models, such as the google_search tool, etc. Maintain and manage daily life data records, and process and present the records.
daily_assistant_agent = Agent(
    name="DailyAssistantAgent",
    model=Gemini(
        model="gemini-2.5-flash-lite",
        retry_options=retry_config
    ),
    instruction = """ You are a specialized daily assistant agent. Your only job is to utilize various tools, agents, ADK, and models, such as the google_search tool, etc. Maintain and manage daily life data records, and process and present the records.""",
    tools=[google_search,],
    output_key="daily_record",  # The result of this agent will be stored in the session state with this key.
)


print("✅ Daily_assistance_agent created.")
# Scheduler Agent: Its job is to utilize various tools, agents, ADK, and models, such as the google_search tool, etc. Maintain and manage daily life data records, and process and present the records.
scheduler_agent = Agent(
    name="SchedulerAgent",
    model=Gemini(
        model="gemini-2.5-flash-lite",
        retry_options=retry_config
    ),
    instruction = """ You are a specialized scheduler agent. Your only job is to utilize various tools, agents, ADK, and models, such as the google_search tool, etc. Maintain and manage daily life data records, and process and present the records.""",
    tools=[google_search,],
    output_key="scheduler_record",  # The result of this agent will be stored in the session state with this key.
)

# Reminder Agent: Its job is to utilize various tools, agents, ADK, and models, such as the google_search tool, etc. Maintain and manage daily life data records, and process and present the records.
reminder_agent = Agent(
    name="ReminderAgent",
    model=Gemini(
        model="gemini-2.5-flash-lite",
        retry_options=retry_config
    ),
    instruction = """ You are a specialized reminder agent. Your only job is to utilize various tools, agents, ADK, and models, such as the google_search tool, etc. Maintain and manage daily life data records, and process and present the records.""",
    tools=[google_search,],
    output_key="reminder_record",  # The result of this agent will be stored in the session state with this key.
)
# Ledger Managing Agent: Its job is to utilize various tools, agents, ADK, and models, such as the google_search tool, etc. Maintain and manage daily life data records, and process and present the records.
ledger_managing_agent = Agent(
    name="DailyAssistantAgent",
    model=Gemini(
        model="gemini-2.5-flash-lite",
        retry_options=retry_config
    ),
    instruction = """ You are a specialized ledger managing agent. Your only job is to utilize various tools, agents, ADK, and models, such as the google_search tool, etc. Maintain and manage daily life data records, and process and present the records.""",
    tools=[google_search,],
    output_key="ledger_record",  # The result of this agent will be stored in the session state with this key.
)
# Daily Assistant Agent: Its job is to utilize various tools, agents, ADK, and models, such as the google_search tool, etc. Maintain and manage daily life data records, and process and present the records.
personal_agent = Agent(
    name="PersonalAgent",
    model=Gemini(
        model="gemini-2.5-flash-lite",
        retry_options=retry_config
    ),
    instruction = """ You are a specialized personal agent. Your only job is to utilize various tools, agents, ADK, and models, such as the google_search tool, etc. Maintain and manage daily life data records, and process and present the records.""",
    tools=[google_search,],
    output_key="personal_record",  # The result of this agent will be stored in the session state with this key.
)
# Daily Assistant Agent: Its job is to utilize various tools, agents, ADK, and models, such as the google_search tool, etc. Maintain and manage daily life data records, and process and present the records.
finance_managing_agent = Agent(
    name="FinanceManagingAgent",
    model=Gemini(
        model="gemini-2.5-flash-lite",
        retry_options=retry_config
    ),
    instruction = """ You are a specialized finance managing agent. Your only job is to utilize various tools, agents, ADK, and models, such as the google_search tool, etc. Maintain and manage daily life data records, and process and present the records.""",
    tools=[google_search,],
    output_key="finance_record",  # The result of this agent will be stored in the session state with this key.
)
# Daily Assistant Agent: Its job is to utilize various tools, agents, ADK, and models, such as the google_search tool, etc. Maintain and manage daily life data records, and process and present the records.
budgeting_agent = Agent(
    name="BudgetingAgent",
    model=Gemini(
        model="gemini-2.5-flash-lite",
        retry_options=retry_config
    ),
    instruction = """ You are a specialized budgeting agent. Your only job is to utilize various tools, agents, ADK, and models, such as the google_search tool, etc. Maintain and manage daily life data records, and process and present the records.""",
    tools=[google_search,],
    output_key="budget_record",  # The result of this agent will be stored in the session state with this key.
)
# Daily Assistant Agent: Its job is to utilize various tools, agents, ADK, and models, such as the google_search tool, etc. Maintain and manage daily life data records, and process and present the records.
planner_agent = Agent(
    name="PlannerAgent",
    model=Gemini(
        model="gemini-2.5-flash-lite",
        retry_options=retry_config
    ),
    instruction = """ You are a specialized planner agent. Your only job is to utilize various tools, agents, ADK, and models, such as the google_search tool, etc. Maintain and manage daily life data records, and process and present the records.""",
    tools=[google_search,],
    output_key="plans_record",  # The result of this agent will be stored in the session state with this key.
)

# To Do List Agent: Its job is to utilize various tools, agents, ADK, and models, such as the google_search tool, etc. Maintain and manage daily life data records, and process and present the records.
to_do_list_agent = Agent(
    name="DailyAssistantAgent",
    model=Gemini(
        model="gemini-2.5-flash-lite",
        retry_options=retry_config
    ),
    instruction = """ You are a specialized 'to-do list managing  agent'. Your only job is to utilize various tools, agents, ADK, and models, such as the google_search tool, etc. Maintain and manage daily life data records, and process and present the records.""",
    tools=[google_search,],
    output_key="todolist_record",  # The result of this agent will be stored in the session state with this key.
)
# Daily Assistant Agent: Its job is to utilize various tools, agents, ADK, and models, such as the google_search tool, etc. Maintain and manage daily life data records, and process and present the records.
not_to_do_list_agent = Agent(
    name="NotToDoListAgent",
    model=Gemini(
        model="gemini-2.5-flash-lite",
        retry_options=retry_config
    ),
    instruction = """ You are a specialized 'not to do list managing agent'. Your only job is to utilize various tools, agents, ADK, and models, such as the google_search tool, etc. Maintain and manage daily life data records, and process and present the records.""",
    tools=[google_search,],
    output_key="nottodolist_record",  # The result of this agent will be stored in the session state with this key.
)

# Daily Assistant Agent: Its job is to utilize various tools, agents, ADK, and models, such as the google_search tool, etc. Maintain and manage daily life data records, and process and present the records.
investment_and_income_managing_agent = Agent(
    name="DailyAssistantAgent",
    model=Gemini(
        model="gemini-2.5-flash-lite",
        retry_options=retry_config
    ),
    instruction = """ You are a specialized investment and income managing agent. Your only job is to utilize various tools, agents, ADK, and models, such as the google_search tool, etc. Maintain and manage daily life data records, and process and present the records.""",
    tools=[google_search,],
    output_key="investment_and_income_record",  # The result of this agent will be stored in the session state with this key.
)
# Daily Assistant Agent: Its job is to utilize various tools, agents, ADK, and models, such as the google_search tool, etc. Maintain and manage daily life data records, and process and present the records.
career_assistance_agent = Agent(
    name="CareerAssistanceAgent",
    model=Gemini(
        model="gemini-2.5-flash-lite",
        retry_options=retry_config
    ),
    instruction = """ You are a specialized career assistance agent. Your only job is to utilize various tools, agents, ADK, and models, such as the google_search tool, etc. Maintain and manage daily life data records, and process and present the records.""",
    tools=[google_search,],
    output_key="career_record",  # The result of this agent will be stored in the session state with this key.
)
# Daily Assistant Agent: Its job is to utilize various tools, agents, ADK, and models, such as the google_search tool, etc. Maintain and manage daily life data records, and process and present the records.
goal_achiever_agent = Agent(
    name="GoalAchieverAgent",
    model=Gemini(
        model="gemini-2.5-flash-lite",
        retry_options=retry_config
    ),
    instruction = """ You are a specialized goal achiever agent. Your only job is to utilize various tools, agents, ADK, and models, such as the google_search tool, etc. Maintain and manage daily life data records, and process and present the records.""",
    tools=[google_search,],
    output_key="goal_record",  # The result of this agent will be stored in the session state with this key.
)
# Education Assistant Agent: Its job is to utilize various tools, agents, ADK, and models, such as the google_search tool, etc. Maintain and manage daily life data records, and process and present the records.
education_agent = Agent(
    name="EducationAgent",
    model=Gemini(
        model="gemini-2.5-flash-lite",
        retry_options=retry_config
    ),
    instruction = """ You are a specialized education assistant agent. Your only job is to utilize various tools, agents, ADK, and models, such as the google_search tool, etc. Maintain and manage daily life data records, and process and present the records.""",
    tools=[google_search,],
    output_key="education_record",  # The result of this agent will be stored in the session state with this key.
)
# Daily Assistant Agent: Its job is to utilize various tools, agents, ADK, and models, such as the google_search tool, etc. Maintain and manage daily life data records, and process and present the records.
exam_preparation_agent = Agent(
    name="ExamPreparationAgent",
    model=Gemini(
        model="gemini-2.5-flash-lite",
        retry_options=retry_config
    ),
    instruction = """ You are a specialized exam preparation assistant agent. Your only job is to utilize various tools, agents, ADK, and models, such as the google_search tool, etc. Maintain and manage daily life data records, and process and present the records.""",
    tools=[google_search,],
    output_key="exam_record",  # The result of this agent will be stored in the session state with this key.
)
# Knowledge Acquire Agent: Its job is to utilize various tools, agents, ADK, and models, such as the google_search tool, etc. Maintain and manage daily life data records, and process and present the records.
knowledge_acquire_agent = Agent(
    name="KnowledgeAcquireAgent",
    model=Gemini(
        model="gemini-2.5-flash-lite",
        retry_options=retry_config
    ),
    instruction = """ You are a specialized knowledge acquire agent. Your only job is to utilize various tools, agents, ADK, and models, such as the google_search tool, etc. Maintain and manage daily life data records, and process and present the records.""",
    tools=[google_search,],
    output_key="knowledge_record",  # The result of this agent will be stored in the session state with this key.
)
