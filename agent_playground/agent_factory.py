from __future__ import annotations

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

from settings import Settings
from tools import get_weather, say_hello, say_goodbye

# TODO: add an agent to get the capital of a country, using an online API
# TODO: merge greetings into single greeting agent with tool selection
# TODO: check if weather can be extracted via online API


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
    )

def build_greeting_agent(settings: Settings) -> Agent:
    """Create a greeting-focused ADK Agent instance.

    Kept as a factory so importing modules doesn't create side effects.
    """
    greeting_agent = Agent(
        # Using a potentially different/cheaper model for a simple task
        model = LiteLlm(model=settings._openai_model),
        name="greeting_agent",
        instruction="You are the Greeting Agent. Your ONLY task is to provide a friendly greeting to the user. "
                    "Use the 'say_hello' tool to generate the greeting. "
                    "If the user provides their name, make sure to pass it to the tool. "
                    "Do not engage in any other conversation or tasks.",
        description="Handles simple greetings and hellos using the 'say_hello' tool.", # Crucial for delegation
        tools=[say_hello],
    )
    print(f"✅ Agent '{greeting_agent.name}' created using model '{greeting_agent.model}'.")
    return greeting_agent

def build_farewell_agent(settings: Settings) -> Agent:
    """Create a farewell-focused ADK Agent instance.

    Kept as a factory so importing modules doesn't create side effects.
    """
    farewell_agent = Agent(
        # Can use the same or a different model
        model = LiteLlm(model=settings._openai_model),
        name="farewell_agent",
        instruction="You are the Farewell Agent. Your ONLY task is to provide a polite goodbye message. "
                    "Use the 'say_goodbye' tool when the user indicates they are leaving or ending the conversation "
                    "(e.g., using words like 'bye', 'goodbye', 'thanks bye', 'see you'). "
                    "Do not perform any other actions.",
        description="Handles simple farewells and goodbyes using the 'say_goodbye' tool.", # Crucial for delegation
        tools=[say_goodbye],
    )
    print(f"✅ Agent '{farewell_agent.name}' created using model '{farewell_agent.model}'.")
    return farewell_agent