from langchain_core.messages import AIMessage, HumanMessage

from hybrid_athlete_ai.agents.coach_graph import get_coach_graph


def chat(message: str, thread_id: str = "default") -> str:
    graph = get_coach_graph()
    result = graph.invoke(
        {"messages": [HumanMessage(content=message)]},
        config={"configurable": {"thread_id": thread_id}},
    )

    messages = result.get("messages", [])
    for message_obj in reversed(messages):
        if isinstance(message_obj, AIMessage) and message_obj.content:
            content = message_obj.content
            if isinstance(content, str):
                return content
            if isinstance(content, list):
                text_parts = [
                    part.get("text", "")
                    for part in content
                    if isinstance(part, dict) and part.get("type") == "text"
                ]
                if text_parts:
                    return "\n".join(text_parts)

    return "I couldn't generate a response. Please try again."
