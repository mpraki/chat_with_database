import operator
from typing import TypedDict, Literal, Annotated

from langchain_core.documents import Document


class Conversation(TypedDict):
    role: Literal['USER', 'ASSISTANT']
    content: str


class AgentState(TypedDict, total=False):
    task: str
    vector_results: list[tuple[Document, float]]
    conversation_history: Annotated[list[Conversation], operator.add]
    user_query_clarification: str
    enhanced_user_query: str
    sql_query_draft: str
    is_draft_query_valid: bool
    reason_for_draft_revision: str
    current_user_query_revision: int #??
    final_result: list[dict] #??
