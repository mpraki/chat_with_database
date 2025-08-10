import os

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langgraph.config import get_stream_writer
from pydantic import SecretStr

from ..agent_state import AgentState
from ..utils.constants import Constants


def search(state: AgentState) -> dict[str, list[tuple[Document, float]]]:
    writer = get_stream_writer()
    writer({Constants.STATE_PROGRESS_UPDATE_KEY: "Finding relevant schemas..."})

    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001",
                                              google_api_key=SecretStr(os.getenv("GOOGLE_API_KEY")))

    collection_name = "sql-schemas"
    persist_directory = f"../vector_stores/{collection_name}"

    vector_db = Chroma(
        persist_directory=persist_directory,
        collection_name=collection_name,
        embedding_function=embeddings
    )

    # Ensure conversation_history exists in state
    if 'conversation_history' not in state or state['conversation_history'] is None or state[
        'conversation_history'] == []:
        history = [HumanMessage(content=state['task'])]  # adding user query to conversation history
    else:
        history = state['conversation_history']
        history.append(HumanMessage(content=state['task']))  # appending user query to conversation history

    user_query_context = (' '.join([
        m.content for m in state.get('conversation_history', [])
        if hasattr(m, 'content') and getattr(m, 'type', None) == 'human'
    ]) + ' ' + state['task'])

    docs_and_scores = vector_db.similarity_search_with_score(query=user_query_context, k=4)
    for doc, score in docs_and_scores:
        print(f"Found document with score: {score} and metadata: {doc.metadata}")

    writer({Constants.STATE_PROGRESS_UPDATE_KEY: "Found relevant schemas..."})
    return {'vector_results': docs_and_scores, 'conversation_history': history}
