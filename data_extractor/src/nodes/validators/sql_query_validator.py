from ...agent_state import AgentState


def validate(state: AgentState) -> bool:
    print(f"Validating SQL query: {state['is_draft_query_valid']}. Reason: {state['reason_for_draft_revision']}")
    return state['is_draft_query_valid'] or False
