import os

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from pydantic import SecretStr

from ..agent_state import AgentState


def search(state: AgentState) -> dict[str, list[tuple[Document, float]]]:
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001",
                                              google_api_key=SecretStr(os.getenv("GOOGLE_API_KEY")))

    collection_name = "sql-schemas"
    persist_directory = f"../vector_stores/{collection_name}"

    vector_db = Chroma(
        persist_directory=persist_directory,
        collection_name=collection_name,
        embedding_function=embeddings
    )

    print(f"Searching for task: {state['task']}")
    print(f"conversation_history - {state['conversation_history']}")

    user_query_context = (' '.join([conversation['content'] for conversation in state.get('conversation_history', []) if
                                    conversation['role'] == 'USER'])
                           + ' ' + state['task'])

    print(f"User query context: {user_query_context}")

    docs_and_scores = vector_db.similarity_search_with_score(query=user_query_context, k=4)
    for doc, score in docs_and_scores:
        print(f"Found document with score: {score} and metadata: {doc.metadata}")

    return {'vector_results': docs_and_scores}
