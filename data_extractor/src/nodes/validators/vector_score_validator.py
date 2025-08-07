from langchain_core.documents import Document
from langgraph.config import get_stream_writer

from ...agent_state import AgentState
from ...utils.constants import Constants


def validate(state: AgentState) -> bool:
    writer = get_stream_writer()
    writer({Constants.STATE_PROGRESS_UPDATE_KEY: "Validating vector search results by score..."})

    vector_results: list[tuple[Document, float]] = state['vector_results']

    # ITERATE vector_results and check if any score is below 0.6
    for doc, score in vector_results:
        if score < Constants.MINIMUM_VECTOR_SCORE:
            print(f"Document {doc.metadata} has a good score: {score}")
            return True

    print("No document has a good score.")
    return False
