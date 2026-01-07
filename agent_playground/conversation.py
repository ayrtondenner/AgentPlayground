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

def save_session_conversation(session_last_update_time: float, conversation_result: dict[str, Any]) -> None:
    session_last_update_time_formatted = datetime.fromtimestamp(session_last_update_time, tz=timezone.utc).isoformat()

    filename = f"{_CONVERSATIONS_FOLDER}/{session_last_update_time_formatted}.json"

    # Ensure folder exists
    os.makedirs(_CONVERSATIONS_FOLDER, exist_ok=True)

    # Windows-safe filename (isoformat contains ":" which is not allowed in filenames)
    filename = filename.replace(":", "-")

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(conversation_result, f, indent=2, ensure_ascii=False)

async def _save_session_conversation(runner: Runner, app_name: str, user_id: str, session_id: str) -> None:
    """Placeholder for saving session conversation if needed."""
    try:
        session = await get_session(runner, app_name, user_id, session_id)

        conversation_result = get_session_conversation(session)

        save_session_conversation(session.last_update_time, conversation_result)

    except Exception as exc:
        print(f"Failed to retrieve session: {exc}")

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


async def run_conversation(*, runner: Runner, app_name: str, user_id: str, session_id: str) -> None:
    print("\nType your message and press Enter. Type 'exit' or 'quit' to stop.")

    # TODO: create an argument to run our test conversation instead of looping
    while True:
        query = await asyncio.to_thread(input, ">>> You: ")
        query = (query or "").strip()

        if not query:
            continue

        # This return only the events for this turn
        conversation_events = await call_agent_async(
            query=query,
            runner=runner,
            user_id=user_id,
            session_id=session_id,
        )

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

        if has_goodbye_call and has_goodbye_response:
            print("Agent said goodbye. Ending conversation.")
            await _save_session_conversation(runner, app_name, user_id, session_id)
            return
