from __future__ import annotations

import asyncio

from google.adk.sessions import InMemorySessionService

from agent_factory import build_weather_agent
from conversation import run_conversation
from runtime import build_runner, init_session
from settings import Settings


async def async_main() -> None:
    settings = Settings()
    settings.validate()

    agent = build_weather_agent(settings)
    session_service = InMemorySessionService()

    await init_session(session_service=session_service, settings=settings)
    runner = build_runner(agent=agent, session_service=session_service, settings=settings)

    await run_conversation(
        runner=runner,
        user_id=settings.user_id,
        session_id=settings.session_id,
    )


def main() -> None:
    try:
        asyncio.run(async_main())
    except Exception as exc:
        print(f"An error occurred: {exc}")


if __name__ == "__main__":
    main()
