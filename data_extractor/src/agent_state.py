from typing import Literal, Annotated, TypedDict
from uuid import uuid4

from langchain_core.documents import Document


class Conversation(TypedDict, total=False):
    role: Literal['USER', 'ASSISTANT']
    content: str
    id: str


def reduce_messages(left: list[Conversation], right: list[Conversation]) -> list[Conversation]:
    # assign ids to messages that don't have them
    for message in right:
        if not message.get("id"):
            message["id"] = str(uuid4())
    # merge the new messages with the existing messages
    merged = left.copy()
    for message in right:
        for i, existing in enumerate(merged):
            # replace any existing messages with the same id
            if existing.get("id") == message.get("id"):
                merged[i] = message
                break
        else:
            # append any new messages to the end
            merged.append(message)
    return merged


class AgentState(TypedDict, total=False):
    task: str
    vector_results: list[tuple[Document, float]]
    conversation_history: Annotated[list[Conversation], reduce_messages]
    user_query_clarification: str
    enhanced_user_query: str
    sql_query_draft: str
    is_draft_query_valid: bool
    reason_for_draft_revision: str
    current_user_query_revision: int  # ??
    final_result: list[dict]
