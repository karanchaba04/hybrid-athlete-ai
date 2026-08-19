from langchain_core.messages import AIMessage, HumanMessage

from hybrid_athlete_ai.agents.coach_graph import get_coach_graph
from hybrid_athlete_ai.services.coach_persistence import add_thread_message, get_thread_messages


def _messages_from_history(thread_id: str, db) -> list:
    history = get_thread_messages(db, thread_id)
    messages = []
    for entry in history:
        if entry.role == "user":
            messages.append(HumanMessage(content=entry.content))
        elif entry.role == "assistant":
            messages.append(AIMessage(content=entry.content))
    return messages


def _extract_response(messages: list) -> str:
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


def chat(message: str, thread_id: str = "default", db=None) -> str:
    graph = get_coach_graph()
    messages = []
    if db is not None:
        messages = _messages_from_history(thread_id, db)
    messages.append(HumanMessage(content=message))

    result = graph.invoke({"messages": messages})
    response = _extract_response(result.get("messages", []))

    if db is not None:
        add_thread_message(db, thread_id=thread_id, role="user", content=message)
        add_thread_message(db, thread_id=thread_id, role="assistant", content=response)

    return response
