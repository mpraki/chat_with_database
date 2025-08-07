from langchain_core.prompts import ChatPromptTemplate
from langgraph.config import get_stream_writer

from ..agent_state import AgentState, Conversation
from ..llm import model
from ..prompts import USER_QUERY_ANALYZER_PROMPT
from ..utils.constants import Constants


def analyze(state: AgentState) -> dict[str, str]:
    writer = get_stream_writer()
    writer({Constants.STATE_PROGRESS_UPDATE_KEY: "Framing question for user query clarification..."})

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
    history.append(Conversation(role="ASSISTANT", content=response.content))

    return {'user_query_clarification': response.content, 'conversation_history': history}


def format_conversation(conversation: list[Conversation]) -> str:
    return "\n".join(f"{c['role']}: {c['content']}" for c in conversation)
