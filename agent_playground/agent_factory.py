from __future__ import annotations

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

from settings import Settings
from tools import get_weather, say_hello, say_goodbye

# TODO: add an agent to get the capital of a country, using an online API
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

def build_greeting_and_farewell_agent(settings: Settings) -> Agent:
    """Create a combined greeting and farewell ADK Agent instance.

    Kept as a factory so importing modules doesn't create side effects.
    """
    greeting_and_farewell_agent = Agent(
        model = LiteLlm(model=settings._openai_model),
        name="greeting_and_farewell_agent",
        instruction="You are the 'Greetings and Farewell Agent'. Your tasks are to provide friendly greetings and polite farewells to the user. "
                    "Use the 'say_hello' tool to generate greetings when the user initiates conversation or says hello. "
                    "Use the 'say_goodbye' tool when the user indicates they are leaving or ending the conversation "
                    "(e.g., using words like 'bye', 'goodbye', 'thanks bye', 'see you'). "
                    "If the user provides their name during greeting, make sure to pass it to the 'say_hello' tool. "
                    "Do not engage in any other conversation or tasks.",
        description="Handles simple greetings and farewells using the 'say_hello' and 'say_goodbye' tools.", # Crucial for delegation
        tools=[say_hello, say_goodbye],
    )
    print(f"✅ Agent '{greeting_and_farewell_agent.name}' created using model '{greeting_and_farewell_agent.model}'.")
    return greeting_and_farewell_agent