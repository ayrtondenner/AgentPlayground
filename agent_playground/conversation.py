from __future__ import annotations

import asyncio

from google.adk.runners import Runner
from google.genai import types


async def call_agent_async(
    *, query: str, runner: Runner, user_id: str, session_id: str
) -> None:
    """Send a query to the agent and print the final response."""
    print(f"\n>>> User Query: {query}")

    content = types.Content(role="user", parts=[types.Part(text=query)])
    final_response_text = "Agent did not produce a final response."

    async for event in runner.run_async(
        user_id=user_id, session_id=session_id, new_message=content
    ):
        if event.is_final_response():
            if event.content and event.content.parts:
                final_response_text = event.content.parts[0].text
            elif event.actions and event.actions.escalate:
                final_response_text = (
                    f"Agent escalated: {event.error_message or 'No specific message.'}"
                )
            break

    print(f"<<< Agent Response: {final_response_text}")


async def run_conversation(*, runner: Runner, user_id: str, session_id: str) -> None:
    print("\nType your message and press Enter. Type 'exit' or 'quit' to stop.")

    while True:
        query = await asyncio.to_thread(input, ">>> You: ")
        query = (query or "").strip()

        if not query:
            continue

        if query.lower() in {"exit", "quit"}:
            print("Exiting conversation.")
            return

        await call_agent_async(
            query=query,
            runner=runner,
            user_id=user_id,
            session_id=session_id,
        )
