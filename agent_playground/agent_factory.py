from __future__ import annotations

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

from settings import Settings
from tools import get_weather


def build_weather_agent(settings: Settings) -> Agent:
    """Create the ADK Agent instance.

    Kept as a factory so importing modules doesn't create side effects.
    """
    return Agent(
        name="weather_agent_v1",
        model=LiteLlm(model=settings.openai_model),
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
