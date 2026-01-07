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

        # type check
        if not event.content or not event.content.parts:
            continue

        for part in event.content.parts:
            if hasattr(part, 'text') and part.text:
                event_content["content"] += part.text

            if hasattr(part, "function_call") and part.function_call:
                event_content["function_calls"].append(part.function_call.to_json_dict())

            if hasattr(part, "function_response") and part.function_response:
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
        conversation_events = await call_agent_async(  # noqa: F841
            query=query,
            runner=runner,
            user_id=user_id,
            session_id=session_id,
        )

        # If we detect a goodbye from the agent, we end the conversation
        session = await get_session(runner, app_name, user_id, session_id)
        is_conversation_ended = session.state.get("conversation_ended", False)

        if is_conversation_ended:
            print("Agent said goodbye. Ending conversation.")
            await _save_session_conversation(runner, app_name, user_id, session_id, test=test)
            return
