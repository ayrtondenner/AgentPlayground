from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any

from google.adk.runners import Runner
from google.adk.sessions import Session
from google.adk.events import Event
from google.genai import types
import json
import os

_CONVERSATIONS_FOLDER = "conversations"

def _load_test_inputs() -> list[str]:
    """Load test inputs from a predefined list or file."""
    test_file = os.path.join(os.path.dirname(__file__), "test_input.txt")

    try:
        with open(test_file, "r", encoding="utf-8") as f:
            lines = f.read().splitlines()
        return lines
    except Exception as exc:
        print(f"Failed to read test inputs from {test_file}: {exc}")
        return []
    
def _detect_goodbye_calls(conversation_events: list[Event]) -> bool:
    """Check whether a conversation contains both a goodbye function call and its corresponding response.
    This function scans a list of Event objects produced by the "greeting_and_farewell_agent".
    Within each event's content parts, it searches for:
    - a function_call with name "say_goodbye"
    - a function_response with name "say_goodbye"

    It returns True only if at least one "say_goodbye" function call and at least one
    matching "say_goodbye" function response are present anywhere in the provided events;
    otherwise, it returns False.

    Args:
        conversation_events (list[Event]): The sequence of conversation events to inspect. Each Event
            should have an `author`, `content`, and `content.parts`. Each part may optionally contain
            `function_call` or `function_response` objects with a `name` attribute.

    Returns:
        bool: True if both a "say_goodbye" call and response are found; False otherwise.
    """
    has_goodbye_call = False
    has_goodbye_response = False

    for ev in conversation_events:
        if ev.author == "greeting_and_farewell_agent" and ev.content and ev.content.parts:
            for part in ev.content.parts:
                if hasattr(part, "function_call") and part.function_call is not None\
                        and part.function_call.name == "say_goodbye":
                    has_goodbye_call = True
                if hasattr(part, "function_response") and part.function_response is not None\
                        and part.function_response.name == "say_goodbye":
                    has_goodbye_response = True

    return has_goodbye_call and has_goodbye_response
    
async def _save_session_conversation(runner: Runner, app_name: str, user_id: str, session_id: str, test: bool = False) -> None:
    """Placeholder for saving session conversation if needed."""
    try:
        session = await get_session(runner, app_name, user_id, session_id)

        conversation_result = get_session_conversation(session)

        save_session_conversation(session.last_update_time, conversation_result, test)

    except Exception as exc:
        print(f"Failed to retrieve session: {exc}")

async def get_session(runner: Runner, app_name: str, user_id: str, session_id: str) -> Session:
    session = await runner.session_service.get_session(
        app_name=app_name, user_id=user_id, session_id=session_id
    )

    assert session is not None, "Session should exist."

    return session

def get_session_conversation(session: Session):
    events = session.events
    conversation_result = {"state": session.state, "conversation": []}

    for event in events:
        
        author = event.author
        event_content = {
            "id": event.id,
            "role": author if author else "unknown",
            "content": "",
            "function_calls": [],
            "function_responses": [],
        }

        if event.content and event.content.parts:
            for part in event.content.parts:
                if hasattr(part, 'text'):
                    text = part.text
                    if text is not None:
                        event_content["content"] += str(text)

                if hasattr(part, "function_call"):
                    function_call = part.function_call
                    if function_call is not None:
                        event_content["function_calls"].append(function_call.to_json_dict())

                if hasattr(part, "function_response"):
                    if part.function_response is not None:
                        event_content["function_responses"].append(part.function_response.to_json_dict())

        conversation_result["conversation"].append(event_content)

    return conversation_result

def save_session_conversation(session_last_update_time: float, conversation_result: dict[str, Any], test: bool = False) -> None:
    session_last_update_time_formatted = datetime.fromtimestamp(session_last_update_time, tz=timezone.utc).isoformat()

    # Examples:
    # If test:      2026-01-07T18-15-39.656681+00-00_TEST.json
    # If not test:  2026-01-07T18-15-39.656681+00-00.json
    filename = f"{_CONVERSATIONS_FOLDER}/{session_last_update_time_formatted}{'_TEST' if test else ''}.json"

    # Ensure folder exists
    os.makedirs(_CONVERSATIONS_FOLDER, exist_ok=True)

    # Windows-safe filename (isoformat contains ":" which is not allowed in filenames)
    filename = filename.replace(":", "-")

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(conversation_result, f, indent=2, ensure_ascii=False)

async def call_agent_async(
    *, query: str, runner: Runner, user_id: str, session_id: str
) -> list[Event]:
    """Send a query to the agent, print the final response, and return all events.

    Returns a list of events yielded by the runner for this turn.
    """
    print(f"\n>>> User Query: {query}")

    content = types.Content(role="user", parts=[types.Part(text=query)])
    final_response_text = "Agent did not produce a final response."
    conversation_events: list[Event] = []

    async for event in runner.run_async(
        user_id=user_id, session_id=session_id, new_message=content
    ):
        conversation_events.append(event)
        if event.is_final_response():
            if event.content and event.content.parts:
                final_response_text = event.content.parts[0].text
            elif event.actions and event.actions.escalate:
                final_response_text = (
                    f"Agent escalated: {event.error_message or 'No specific message.'}"
                )
            break

    print(f"<<< Agent Response: {final_response_text}")
    return conversation_events


async def run_conversation(*, runner: Runner, app_name: str, user_id: str, session_id: str, test: bool = False) -> None:
    
    input_lines: list[str] = _load_test_inputs() if test else []
    input_generator = (line for line in input_lines)
    release_env = not test
    
    print("\nType your message and press Enter. Type 'exit' or 'quit' to stop.")

    # If test mode, use predefined inputs; else, use interactive input via endless loop
    while release_env or (line := next(input_generator, None)) is not None:
        query = await asyncio.to_thread(input, ">>> You: ") if release_env else line # type: ignore
        query = (query or "").strip()

        if not release_env:
            print(f">>> You: {query}") # Echo the test input

        if not query:
            continue

        # This return only the events for this turn
        conversation_events = await call_agent_async(
            query=query,
            runner=runner,
            user_id=user_id,
            session_id=session_id,
        )

        # If we detect a goodbye from the agent, we end the conversation
        is_agent_goodbye = _detect_goodbye_calls(conversation_events)

        if is_agent_goodbye:
            print("Agent said goodbye. Ending conversation.")
            await _save_session_conversation(runner, app_name, user_id, session_id, test=test)
            return
