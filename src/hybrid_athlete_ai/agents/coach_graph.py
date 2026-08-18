from langchain_anthropic import ChatAnthropic
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

from hybrid_athlete_ai.agents.llm import get_coach_llm
from hybrid_athlete_ai.agents.prompts import COACH_SYSTEM_PROMPT
from hybrid_athlete_ai.agents.tools import COACH_TOOLS

_checkpointer = MemorySaver()
_coach_graph = None


def build_coach_graph():
    return create_react_agent(
        get_coach_llm(),
        COACH_TOOLS,
        prompt=COACH_SYSTEM_PROMPT,
        checkpointer=_checkpointer,
        name="hybrid-athlete-coach",
    )


def get_coach_graph():
    global _coach_graph
    if _coach_graph is None:
        _coach_graph = build_coach_graph()
    return _coach_graph


def reset_coach_graph() -> None:
    """Clear cached graph (useful in tests and after config changes)."""
    global _coach_graph
    _coach_graph = None
