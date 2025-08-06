from langchain_core.prompts import ChatPromptTemplate

from ..agent_state import AgentState
from ..llm import model
from ..prompts import USER_QUERY_ENHANCER_PROMPT


def plan(state: AgentState) -> dict:
    print("Enhancing user query...")
    # Collect all document page contents into a list
    db_schema = [doc.page_content for doc, _ in state['vector_results']]

    prompt_template = ChatPromptTemplate.from_template(USER_QUERY_ENHANCER_PROMPT)
    prompt = prompt_template.invoke({"db_schema": db_schema, "conversation_history": state['conversation_history']})
    response = model().invoke(prompt)

    return {'enhanced_user_query': response.content}
