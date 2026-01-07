from __future__ import annotations

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

from settings import Settings
from tools import get_weather, get_local_time, say_hello, say_goodbye

def build_root_agent(settings: Settings) -> Agent:
    """Create the root ADK Agent instance.

    Kept as a factory so importing modules doesn't create side effects.
    """
    return Agent(
        name="root_agent",
        model=LiteLlm(model=settings._openai_model),
        description="The root agent that delegates to sub-agents.",
        instruction=
    """You are the root agent. You are the main coordinator of the conversation.
    You are coordinating a team. Your task is to delegate user requests to the appropriate agent.

    You have specialized sub-agents:
    - The 'weather_agent_v1' which provides weather information for specific cities.
    - The 'local_time_agent_v1' which provides local time for specific cities.
    - The 'greeting_and_farewell_agent' which handles greetings ('hi', 'hello') and farewells ('bye', 'see you').

    Analyze the user's query.
    If it's a weather request, delegate it to the 'weather_agent_v1'.
    If it's a local time request, delegate it to the 'local_time_agent_v1'.
    If it's a greeting or farewell, delegate it to the 'greeting_and_farewell_agent'.
    For anything else, respond appropriately or state you cannot handle it""",
        sub_agents=[
            build_weather_agent(settings),
            build_local_time_agent(settings),
            build_greeting_and_farewell_agent(settings),
        ],
    )

# TODO: check if weather can be extracted via online API.
# Example: Open-Meteo - Free with no API key required
# OpenWeatherMap - Widely used in tutorials, offers a free plan for non-commercial use with limits (e.g., 1,000 calls/day for one call 3.0 API).
def build_weather_agent(settings: Settings) -> Agent:
    """Create the ADK Agent instance.

    Kept as a factory so importing modules doesn't create side effects.
    """
    return Agent(
        name="weather_agent_v1",
        model=LiteLlm(model=settings._openai_model),
        description="Provides weather information for specific cities.",
        instruction=(
            "You are a helpful weather assistant. "
            "When the user asks for the weather in a specific city, "
            "use the 'get_weather' tool to find the information. "
            "If the tool returns an error, inform the user politely. "
            "If the tool is successful, present the weather report clearly."
        ),
        tools=[get_weather],
        output_key="weather_agent_response",
    )

def build_local_time_agent(settings: Settings) -> Agent:
    """Create the ADK Agent instance.

    Kept as a factory so importing modules doesn't create side effects.
    """
    return Agent(
        name="local_time_agent_v1",
        model=LiteLlm(model=settings._openai_model),
        description="Provides local time information for specific cities.",
        instruction=(
            "You are a helpful assistant that provides local time for specific cities. "
            "When the user asks for the local time in a specific city, "
            "use the 'get_local_time' tool to find the information. "
            "If the tool returns an error, inform the user politely. "
            "If the tool is successful, present the local time clearly."
        ),
        tools=[get_local_time],
        output_key="local_time_agent_response",
    )

def build_greeting_and_farewell_agent(settings: Settings) -> Agent:
    """Create a combined greeting and farewell ADK Agent instance.

    Kept as a factory so importing modules doesn't create side effects.
    """
    greeting_and_farewell_agent = Agent(
        model = LiteLlm(model=settings._openai_model),
        name="greeting_and_farewell_agent",
        instruction="You are the 'Greetings and Farewell Agent'. Your tasks are to provide friendly greetings and polite farewells to the user. "
                    "Use the 'say_hello' tool to generate greetings when the user initiates conversation or says hello. "
                    "For 'say_hello', if the user provides their name, make sure to pass it to the tool. "
                    "Otherwise, try to get from property 'user_name' by session stored state if available. "
                    "Use the 'say_goodbye' tool when the user indicates they are leaving or ending the conversation "
                    "(e.g., using words like 'bye', 'goodbye', 'thanks bye', 'see you'). "
                    "If the user provides their name during greeting, make sure to pass it to the 'say_hello' tool. "
                    "Do not engage in any other conversation or tasks.",
        description="Handles simple greetings and farewells using the 'say_hello' and 'say_goodbye' tools.", # Crucial for delegation
        tools=[say_hello, say_goodbye],
    )
    print(f"✅ Agent '{greeting_and_farewell_agent.name}' created using model '{greeting_and_farewell_agent.model}'.")
    return greeting_and_farewell_agent