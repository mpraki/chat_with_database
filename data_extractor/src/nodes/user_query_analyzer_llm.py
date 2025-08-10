from langchain_core.messages import BaseMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langgraph.config import get_stream_writer
from langgraph.errors import GraphRecursionError

from ..agent_state import AgentState
from ..llm import model
from ..prompts import USER_QUERY_ANALYZER_PROMPT
from ..utils.constants import Constants


def analyze(state: AgentState) -> dict[str, str]:
    writer = get_stream_writer()
    writer({Constants.STATE_PROGRESS_UPDATE_KEY: "Framing question for user query clarification..."})

    current_user_query_revision = state.get('current_user_query_revision', 0) + 1
    if current_user_query_revision > Constants.USER_QUERY_MAX_REVISIONS:
        raise GraphRecursionError(f"Exceeded maximum query revisions: {Constants.USER_QUERY_MAX_REVISIONS}")

    schema_summary = ''
    # Read schema summary from the relative path
    with open("../schema_summary.txt", "r") as f:
        schema_summary = f.read()

    history = state['conversation_history']

    # Format the conversation history for the prompt
    conversation_str = format_conversation(history)

    prompt_template = ChatPromptTemplate.from_template(USER_QUERY_ANALYZER_PROMPT)
    prompt = prompt_template.invoke({"schema_summary": schema_summary, "conversation": conversation_str})

    response = model().invoke(prompt)

    # Add the response to the conversation history
    history.append(AIMessage(content=response.content))

    writer({Constants.STATE_PROGRESS_UPDATE_KEY: "Framed question for user query clarification..."})

    return {'user_query_clarification': response.content, 'conversation_history': history,
            'current_user_query_revision': current_user_query_revision}


def format_conversation(conversation: list[BaseMessage]) -> str:
    lines = []
    for c in conversation:
        if getattr(c, 'type', None) == 'human':
            lines.append(f"USER: {c.content}")
        elif getattr(c, 'type', None) == 'ai':
            lines.append(f"ASSISTANT: {c.content}")
    return "\n".join(lines)
