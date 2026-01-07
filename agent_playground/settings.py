from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_name: str = "weather_tutorial_app"
    user_id: str = "user_1"
    session_id: str = "session_001"

    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "")

    def validate(self) -> None:
        # OPENAI_API_KEY may or may not be required depending on your LiteLLM setup.
        if not self.openai_model:
            raise ValueError(
                "OPENAI_MODEL is not set. Add it to your environment or .env (e.g., OPENAI_MODEL=gpt-4o-mini)."
            )
