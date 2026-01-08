from __future__ import annotations

from .agent_factory import build_root_agent
from .runtime import build_initial_state # noqa: F401
from .settings import Settings

settings = Settings()
settings.validate()

# ADK CLI (`adk run`, `adk web`) looks for a top-level `root_agent` (or `app`) symbol.
root_agent = build_root_agent(settings)

# This is the same state payload used by `agent_playground.runtime.init_session(...)`.
# Note: session creation itself is owned by the runtime (CLI / API server / web UI).
# default_session_state = build_initial_state(settings)