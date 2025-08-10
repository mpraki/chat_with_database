from typing import Annotated, TypedDict
from uuid import uuid4

from langchain_core.documents import Document
from langchain_core.messages import BaseMessage


def reduce_messages(left: list[BaseMessage], right: list[BaseMessage]) -> list[BaseMessage]:
    # assign ids to messages that don't have them (using .id property if available, else add as custom attribute)
    for message in right:
        if not hasattr(message, 'id') or getattr(message, 'id', None) is None:
            setattr(message, 'id', str(uuid4()))
    # merge the new messages with the existing messages
    merged = left.copy()
    for message in right:
        message_id = getattr(message, 'id', None)
        for i, existing in enumerate(merged):
            existing_id = getattr(existing, 'id', None)
            if existing_id == message_id:
                merged[i] = message
                break
        else:
            merged.append(message)
    return merged


class AgentState(TypedDict, total=False):
    task: str
    vector_results: list[tuple[Document, float]]
    conversation_history: Annotated[list[BaseMessage], reduce_messages]
    user_query_clarification: str
    enhanced_user_query: str
    sql_query_draft: str
    is_draft_query_valid: bool
    reason_for_draft_revision: str
    current_user_query_revision: int
    current_draft_revision: int
    final_result: list[dict]
