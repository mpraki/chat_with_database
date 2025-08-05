from langchain_core.documents import Document

from ...agent_state import AgentState


def validate(state: AgentState) -> bool:
    vector_results: list[tuple[Document, float]] = state['vector_results']

    # ITERATE vector_results and check if any score is below 0.6
    for doc, score in vector_results:
        if score < 0.6:
            print(f"Document {doc.page_content} has a good score: {score}")
            return True

    print("No document has a good score.")
    return False
