from langchain_core.prompts import ChatPromptTemplate
from langgraph.config import get_stream_writer

from ..agent_state import AgentState
from ..llm import model
from ..prompts import USER_QUERY_ENHANCER_PROMPT
from ..utils.constants import Constants


def plan(state: AgentState) -> dict:
    writer = get_stream_writer()
    writer({Constants.STATE_PROGRESS_UPDATE_KEY: "Enhancing user query..."})
    print("Enhancing user query...")
    # Collect all document page contents into a list
    db_schema = [doc.page_content for doc, _ in state['vector_results']]

    prompt_template = ChatPromptTemplate.from_template(USER_QUERY_ENHANCER_PROMPT)
    prompt = prompt_template.invoke({"db_schema": db_schema, "conversation_history": state['conversation_history']})
    response = model().invoke(prompt)

    writer({Constants.STATE_PROGRESS_UPDATE_KEY: "User query enhancement complete."})
    return {'enhanced_user_query': response.content}
