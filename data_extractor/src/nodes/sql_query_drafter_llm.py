from langchain_core.prompts import ChatPromptTemplate

from ..agent_state import AgentState
from ..llm import model
from ..prompts import SQL_QUERY_DRAFTER_PROMPT


def draft(state: AgentState) -> dict:
    print(f"Drafting SQL query for state: {state['enhanced_user_query']}")
    # Collect all document page contents into a list
    db_schema = [doc.page_content for doc, _ in state['vector_results']]

    prompt_template = ChatPromptTemplate.from_template(SQL_QUERY_DRAFTER_PROMPT)
    prompt = prompt_template.invoke({"db_schema": db_schema, "query_plan": state['enhanced_user_query']})
    response = model().invoke(prompt)

    return {'sql_query_draft': response.content}
