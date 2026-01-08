# AgentPlayground
A quick playground for AI agents development.

This project is currently a minimal Google ADK-based "weather agent" example.

## Layout

- `agent_playground/` — package code (agent factory, tools, runtime, conversation loop)
- `__main__.py` — root shim entrypoint (kept for convenience)
- `tools.py` — compatibility shim (re-exports `agent_playground.tools`)

## Requirements

- Python 3.11+
- A configured environment with Google ADK + dependencies installed

## Setup

Pick one of the following:

### Option A: Conda (recommended)

```powershell
conda env create -f environment.yml
conda activate agent-playground
python -m agent_playground
```

### Option B: venv + pip

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m agent_playground
```

## Environment variables

- `OPENAI_MODEL` (required): model name used by `LiteLlm` (example: `gpt-4o-mini`)
- `OPENAI_API_KEY` (may be required depending on your LiteLLM/provider setup)

Tip: you can set these in PowerShell for the current session:

```powershell
$env:OPENAI_MODEL = "gpt-4o-mini"
$env:OPENAI_API_KEY = "..."
```

Alternatively, copy `.env.example` to `.env` and fill in your values.

## Run

Recommended:

```powershell
python -m agent_playground
```

Alternative (kept for backwards compatibility):

```powershell
python __main__.py
```

Once running, type messages into the terminal. Use `exit` or `quit` to stop.

## Run with ADK Web UI

The ADK CLI discovers agents by scanning subfolders for an `agent.py` that exports a top-level `root_agent`.
This repo provides that entrypoint at `agent_playground/agent.py`.

From the repo root (the parent folder that contains `agent_playground/`), run:

```powershell
adk web --port 8000
```

Then open http://localhost:8000 and select `agent_playground`.
