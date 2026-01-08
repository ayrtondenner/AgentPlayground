from __future__ import annotations

import asyncio
import argparse

from google.adk.sessions import InMemorySessionService

from .agent_factory import build_root_agent
from .conversation import run_conversation
from .runtime import build_runner, init_session
from .settings import Settings

async def async_main(*, test: bool = False) -> None:
    settings = Settings()
    settings.validate()

    agent = build_root_agent(settings)
    session_service = InMemorySessionService()

    await init_session(session_service=session_service, settings=settings)
    runner = build_runner(agent=agent, session_service=session_service, settings=settings)

    await run_conversation(
        runner=runner,
        app_name=settings.app_name,
        user_id=settings.user_id,
        session_id=settings.session_id,
        test=test,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Agent Playground Runner")
    parser.add_argument("--test", action="store_true", help="Run scripted test inputs instead of interactive mode")
    args = parser.parse_args()
    test = bool(args.test)
    try:
        asyncio.run(async_main(test=test))
    except Exception as exc:
        print(f"An error occurred: {exc}")

if __name__ == "__main__":
    main()
