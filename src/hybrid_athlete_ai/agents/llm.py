from langchain_anthropic import ChatAnthropic

from hybrid_athlete_ai.config import settings

# Claude 4.6+ models reject the temperature parameter on the Messages API.
_TEMPERATURE_UNSUPPORTED_PREFIXES = (
    "claude-opus-5",
    "claude-sonnet-5",
    "claude-fable-5",
    "claude-opus-4-",
    "claude-sonnet-4-",
)


def supports_temperature(model: str) -> bool:
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
    if supports_temperature(settings.coach_model):
        llm_kwargs["temperature"] = settings.coach_temperature

    return ChatAnthropic(**llm_kwargs)
