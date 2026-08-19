import json
from typing import Any, TypedDict

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph

from hybrid_athlete_ai.agents.llm import get_coach_llm
from hybrid_athlete_ai.agents.prompts import ACCESSORY_SYSTEM_PROMPT
from hybrid_athlete_ai.schemas.coach import AccessoryRecommendation


class AccessoryGraphState(TypedDict):
    available_slots: list[str]
    notes: str | None
    context: dict[str, Any]
    recommendation: AccessoryRecommendation | None


def recommend_accessories(state: AccessoryGraphState) -> dict[str, Any]:
    slots_text = "\n".join(f"- {slot}" for slot in state["available_slots"])
    context_json = json.dumps(state["context"], indent=2, default=str)
    user_notes = state.get("notes") or "None"

    user_prompt = f"""
Available accessory slots:
{slots_text}

Additional notes from athlete:
{user_notes}

Training context (JSON):
{context_json}

Build one accessory plan per available slot. Respect time available in each slot label.
""".strip()

    llm = get_coach_llm().with_structured_output(AccessoryRecommendation)
    recommendation = llm.invoke(
        [
            SystemMessage(content=ACCESSORY_SYSTEM_PROMPT),
            HumanMessage(content=user_prompt),
        ]
    )
    return {"recommendation": recommendation}


def build_accessory_graph():
    graph = StateGraph(AccessoryGraphState)
    graph.add_node("recommend_accessories", recommend_accessories)
    graph.add_edge(START, "recommend_accessories")
    graph.add_edge("recommend_accessories", END)
    return graph.compile()


_accessory_graph = None


def get_accessory_graph():
    global _accessory_graph
    if _accessory_graph is None:
        _accessory_graph = build_accessory_graph()
    return _accessory_graph


def reset_accessory_graph() -> None:
    global _accessory_graph
    _accessory_graph = None


def recommend_accessory_workouts(
    *,
    available_slots: list[str],
    notes: str | None = None,
    context: dict[str, Any],
) -> AccessoryRecommendation:
    graph = get_accessory_graph()
    result = graph.invoke(
        {
            "available_slots": available_slots,
            "notes": notes,
            "context": context,
            "recommendation": None,
        }
    )
    recommendation = result.get("recommendation")
    if recommendation is None:
        raise RuntimeError("Accessory graph did not produce a recommendation.")
    return recommendation
