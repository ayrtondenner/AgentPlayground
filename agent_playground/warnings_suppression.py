from __future__ import annotations

import os
import warnings


def _env_truthy(name: str, default: str = "1") -> bool:
    value = os.environ.get(name, default).strip().lower()
    return value in {"1", "true", "yes", "y", "on"}


def check_pydantic_warnings_suppression() -> None:
    """Optionally suppress noisy Pydantic serializer warnings.

    1) What's happening?
       When using ADK's `LiteLlm` adapter, ADK calls `litellm.acompletion(...)`
       and receives a LiteLLM `ModelResponse` with `choices[*].message`.
       In some versions/combinations, LiteLLM returns “OpenAI-like” objects
       whose runtime shape does not exactly match what Pydantic v2 expects to
       serialize.

       As a result, Pydantic emits warnings like:
         - "Pydantic serializer warnings:"
         - "serialized value may not be as expected"

       Important: this is NOT an error. It's a warning that effectively says:
       “I serialized something that didn’t match the schema I expected”.

    2) Why do we still get correct answers?
       ADK still successfully extracts the relevant fields it needs (e.g.
       text content and tool calls). The warning happens during serialization
       of some intermediate objects, not during the agent's actual reasoning
       or tool execution.

    3) How are we "fixing" it now?
       We suppress ONLY these specific Pydantic serializer warnings at process
       startup, controlled by the env var:
         `AGENT_PLAYGROUND_SUPPRESS_PYDANTIC_SERIALIZER_WARNINGS`

       This keeps logs clean without hiding unrelated warnings.

    4) Alternatives (if we want a different approach later)
       - Change LiteLLM version (upgrade/downgrade) to a combination that
         avoids the serialization mismatch.
       - Avoid LiteLLM for the affected models and use ADK's native model
         integration where available.
       - Narrow the filter further or route warnings to a structured logger.

    Defaults to ON (`true`/`1`). Set to `false`/`0` to re-enable.
    """

    if not _env_truthy("AGENT_PLAYGROUND_SUPPRESS_PYDANTIC_SERIALIZER_WARNINGS", "1"):
        return

    warnings.filterwarnings(
        "ignore",
        message=r"^Pydantic serializer warnings:.*",
        category=UserWarning,
        module=r"pydantic(\..*)?$",
    )
