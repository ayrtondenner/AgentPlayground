from __future__ import annotations

import os
import uuid
from dataclasses import dataclass

@dataclass(frozen=True)
class Settings:
    app_name: str = "weather_tutorial_app"
    session_id: str = str(uuid.uuid4())
    user_id: str = "1"
    user_name: str = "Ayrton Denner"
    user_email: str = "ayrtondenner_2013@hotmail.com"

    _openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    _openai_model: str = os.getenv("OPENAI_MODEL", "")

    def validate(self) -> None:
        # OPENAI_API_KEY may or may not be required depending on your LiteLLM setup.
        if not self._openai_model:
            raise ValueError(
                "OPENAI_MODEL is not set. Add it to your environment or .env (e.g., OPENAI_MODEL=gpt-4o-mini)."
            )
