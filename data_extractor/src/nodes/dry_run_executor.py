import os

from ..agent_state import AgentState
from ..utils.mysql_util import run_execute_plan_query


def execute(state: AgentState) -> dict:
    print("Executing dry run executor with query:", state['sql_query_draft'])

    results = run_execute_plan_query(state['sql_query_draft'])

    return {'is_draft_query_valid': results['success'], 'reason_for_draft_revision': results['error']}
