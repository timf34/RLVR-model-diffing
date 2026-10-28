"""Generate Bloom scenarios with Sonnet 5.5 pinned to Anthropic on OpenRouter.

Sonnet/Opus 5.5 reject forced tool calls (tool_choice="tool"), which Bloom's
understanding/ideation stages use. We send tool_choice="auto" instead; Bloom
already retries if the model answers without calling the submit tool.
"""
import sys
from dotenv import load_dotenv
from inspect_ai.model import get_model
from inspect_ai.tool import ToolFunction
from petri_bloom import run_scenarios

load_dotenv("../.env")
model = get_model(
    "openrouter/anthropic/claude-sonnet-5.5",
    provider={"only": ["anthropic"], "allow_fallbacks": False},
)
_generate = model.generate


async def generate_auto(*args, tool_choice=None, **kwargs):
    if isinstance(tool_choice, ToolFunction):
        tool_choice = "auto"
    return await _generate(*args, tool_choice=tool_choice, **kwargs)


model.generate = generate_auto
run_scenarios(sys.argv[1], scenarios_model=model, overwrite="--overwrite" in sys.argv)
