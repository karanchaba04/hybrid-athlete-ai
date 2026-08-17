from langchain_anthropic import ChatAnthropic
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

from hybrid_athlete_ai.agents.prompts import COACH_SYSTEM_PROMPT
from hybrid_athlete_ai.agents.tools import COACH_TOOLS
from hybrid_athlete_ai.config import settings


_checkpointer = MemorySaver()
_coach_graph = None

# Claude 4.6+ models reject the temperature parameter on the Messages API.
_TEMPERATURE_UNSUPPORTED_PREFIXES = (
    "claude-opus-5",
    "claude-sonnet-5",
    "claude-fable-5",
    "claude-opus-4-",
    "claude-sonnet-4-",
)


def _supports_temperature(model: str) -> bool:
    return not any(model.startswith(prefix) for prefix in _TEMPERATURE_UNSUPPORTED_PREFIXES)


def get_coach_llm() -> ChatAnthropic:
    if not settings.anthropic_api_key:
        raise ValueError(
            "ANTHROPIC_API_KEY is not set. Add it to .env to use the AI coach."
        )

    llm_kwargs: dict = {
        "model": settings.coach_model,
        "api_key": settings.anthropic_api_key,
    }
    if _supports_temperature(settings.coach_model):
        llm_kwargs["temperature"] = settings.coach_temperature

    return ChatAnthropic(**llm_kwargs)


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
