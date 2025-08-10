from langchain_core.prompts import ChatPromptTemplate
from langgraph.config import get_stream_writer
from langgraph.errors import GraphRecursionError

from ..agent_state import AgentState
from ..llm import model
from ..prompts import SQL_QUERY_DRAFTER_PROMPT, SQL_QUERY_DRAFT_REVISION_PROMPT
from ..utils.constants import Constants


def draft(state: AgentState) -> dict:
    writer = get_stream_writer()
    writer({Constants.STATE_PROGRESS_UPDATE_KEY: "Drafting SQL query..."})
    print(f"Drafting SQL query for state: {state['enhanced_user_query']}")

    current_draft_revision = state.get('current_draft_revision', 0) + 1
    if current_draft_revision > Constants.MAX_DRAFT_REVISION:
        raise GraphRecursionError(f"Exceeded maximum draft revisions: {Constants.MAX_DRAFT_REVISION}")

    # Collect all document page contents into a list
    db_schema = [doc.page_content for doc, _ in state['vector_results']]
    if 'is_draft_query_valid' not in state or state['is_draft_query_valid'] is None or state[
        'is_draft_query_valid'] == [] or state['is_draft_query_valid'] == True:
        prompt_template = ChatPromptTemplate.from_template(SQL_QUERY_DRAFTER_PROMPT)
        prompt = prompt_template.invoke({"db_schema": db_schema, "query_plan": state['enhanced_user_query']})

    else:
        prompt_template = ChatPromptTemplate.from_template(SQL_QUERY_DRAFT_REVISION_PROMPT)
        prompt = prompt_template.invoke(
            {"db_schema": db_schema, "query_plan": state['enhanced_user_query'], "sql_query": state['sql_query_draft'],
             "identified_issues": state['reason_for_draft_revision']})

    response = model().invoke(prompt)

    writer({Constants.STATE_PROGRESS_UPDATE_KEY: "SQL query draft complete."})
    return {'sql_query_draft': response.content, 'current_draft_revision': current_draft_revision}
