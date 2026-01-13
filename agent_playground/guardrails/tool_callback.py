# Ensure necessary imports are available
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext
from typing import Optional, Dict, Any # For type hints

def block_springfield_tool_guardrail(
    tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext
) -> Optional[Dict]:
    """
    Checks if 'get_weather' is called for 'Springfield'.
    If so, blocks the tool execution and returns a specific error dictionary.
    Otherwise, allows the tool call to proceed by returning None.
    """
    tool_name = tool.name
    agent_name = tool_context.agent_name # Agent attempting the tool call
    print(f"--- Callback: block_springfield_tool_guardrail running for tool '{tool_name}' in agent '{agent_name}' ---")
    print(f"--- Callback: Inspecting args: {args} ---")

    # --- Guardrail Logic ---
    target_tool_name = "get_weather" # Match the function name used by FunctionTool
    blocked_city = "springfield"

    # Early exits for non-target tools or non-blocked cities
    # Returning None allows the actual tool function to run
    if tool_name != target_tool_name:
        print(f"--- Callback: Tool '{tool_name}' is not the target tool. Allowing. ---")
        return None

    city_argument = str(args.get("city", "")).strip()
    if not city_argument:
        print(f"--- Callback: No city provided for tool '{tool_name}'. Allowing. ---")
        return None

    if city_argument.lower() != blocked_city:
        print(f"--- Callback: City '{city_argument}' is allowed for tool '{tool_name}'. ---")
        return None

    # Blocked case
    print(f"--- Callback: Detected blocked city '{city_argument}'. Blocking tool execution! ---")
    # Optionally update state
    tool_context.state["guardrail_tool_block_triggered"] = True
    print("--- Callback: Set state 'guardrail_tool_block_triggered': True ---")

    # Return a dictionary matching the tool's expected output format for errors
    # This dictionary becomes the tool's result, skipping the actual tool run.
    return {
        "status": "error",
        "error_message": (
            f"Policy restriction: Weather checks for '{city_argument.capitalize()}' "
            "are currently disabled by a tool guardrail."
        ),
    }

print("✅ block_springfield_tool_guardrail function defined.")