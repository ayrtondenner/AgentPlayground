from __future__ import annotations

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService, Session

from settings import Settings


async def init_session(
    *, session_service: InMemorySessionService, settings: Settings
) -> Session:

    # Saving all non-private settings into the session state
    data = vars(settings)
    initial_state = {k: v for k, v in data.items() if not k.startswith("_")}

    session = await session_service.create_session(
        app_name=settings.app_name,
        user_id=settings.user_id,
        session_id=settings.session_id,
        state=initial_state,
    )

    print(
        f"Session created: App='{settings.app_name}', User='{settings.user_id}', Session='{settings.session_id}'"
    )
    return session


def build_runner(*, agent, session_service: InMemorySessionService, settings: Settings) -> Runner:
    runner = Runner(
        agent=agent,
        app_name=settings.app_name,
        session_service=session_service,
    )
    print(f"Runner created for agent '{runner.agent.name}'.")
    return runner
