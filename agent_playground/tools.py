from typing import Optional, TypedDict
from datetime import datetime, timedelta, timezone

from google.adk.tools.tool_context import ToolContext

from .settings import Settings


class CityData(TypedDict):
    """Structured data for a supported city in this mock tool set.

    Keys:
        weather: Human-readable weather report for the city.
        utc_offset_hours: Fixed offset from UTC in hours (does not account for DST).
    """
    weather: str
    utc_offset_hours: int


CITY_DATA: dict[str, CityData] = {
    "newyork": {
        "weather": "The weather in New York is sunny with a temperature of 25°C.",
        "utc_offset_hours": -5,
    },
    "london": {
        "weather": "It's cloudy in London with a temperature of 15°C.",
        "utc_offset_hours": 0,
    },
    "tokyo": {
        "weather": "Tokyo is experiencing light rain and a temperature of 18°C.",
        "utc_offset_hours": 9,
    },
}

def get_weather(city: str) -> dict:
    """Retrieves the current weather report for a specified city.

    Args:
        city: The name of the city (e.g., "New York", "London", "Tokyo").

    Returns:
        dict: Includes a 'status' key ('success' or 'error').
              If 'success', includes a 'report' key.
              If 'error', includes an 'error_message' key.
    """
    print(f"--- Tool: get_weather called for city: {city} ---")
    city_normalized = city.lower().replace(" ", "")

    city_data = CITY_DATA.get(city_normalized)
    if city_data:
        return {
            "status": "success",
            "report": city_data["weather"],
        }

    return {
        "status": "error",
        "error_message": f"Sorry, I don't have weather information for '{city}'.",
    }

def get_local_time(city: str) -> dict:
    """Retrieves the current local time for a specified city.

    Uses mocked city support (New York, London, Tokyo) but performs real timezone
    conversion from UTC using fixed offsets.

    Args:
        city: The name of the city (e.g., "New York", "London", "Tokyo").

    Returns:
        dict: Includes a 'status' key ('success' or 'error').
              If 'success', includes a 'report' key.
              If 'error', includes an 'error_message' key.
    """
    print(f"--- Tool: get_local_time called for city: {city} ---")
    city_normalized = city.lower().replace(" ", "")

    # Fixed UTC offsets for this mock tool.
    # Note: This intentionally does not model daylight saving time.
    city_data = CITY_DATA.get(city_normalized)
    if not city_data:
        return {
            "status": "error",
            "error_message": f"Sorry, I don't have local time information for '{city}'.",
        }

    utc_now = datetime.now(timezone.utc)
    local_tz = timezone(timedelta(hours=city_data["utc_offset_hours"]))
    local_time = utc_now.astimezone(local_tz)
    offset = city_data["utc_offset_hours"]
    offset_label = f"UTC{offset:+d}"

    return {
        "status": "success",
        "report": (
            f"The local time in {city.strip()} is "
            f"{local_time.strftime('%Y-%m-%d %H:%M:%S')} ({offset_label})."
        ),
    }

def say_hello(tool_context: ToolContext, name: Optional[str] = None) -> str:
    """Provides a simple greeting.
    If a name is provided, it will be used. Defaults to a generic greeting if not provided.

    Name resolution order (most specific to least specific):
    1) Use the explicit `name` argument (typically extracted from the user's message).
    2) Otherwise, fall back to `tool_context.state["user_name"]`.

    Args:
        name (str, optional): The name of the person to greet.
            If omitted, the tool will attempt to use `tool_context.state["user_name"]`.

    Returns:
        str: A friendly greeting message.
    """

    # ADK Web may create sessions without any initial state. If so, fall back to
    # our local Settings default and persist it into the session state so future
    # turns/tools can use it.
    name = name or tool_context.state.get("user_name", None) or Settings().user_name

    if name:
        greeting = f"Hello, {name}!"
        print(f"--- Tool: say_hello called with name: {name} ---")
    else:
        greeting = "Hello there!" # Default greeting if name is None or not explicitly passed
        print("--- Tool: say_hello called without a specific name ---")
    return greeting

def say_goodbye(tool_context: ToolContext) -> str:
    """Provides a simple farewell message to conclude the conversation."""
    print("--- Tool: say_goodbye called ---")
    hour = datetime.now().hour
    if hour < 12:
        part_of_day = "morning"
    elif hour < 18:
        part_of_day = "afternoon"
    else:
        part_of_day = "night"

    tool_context.state["conversation_ended"] = True

    return f"Goodbye! Have a great {part_of_day}."
