import os

from ..agent_state import AgentState
from ..utils.azure_sql_util import get_azure_sql_connection, run_execute_plan_query


def execute(state: AgentState) -> dict:
    print("Executing dry run executor with state:", state)
    engine = get_azure_sql_connection(os.getenv("DATABASE_URL"),
                                      os.getenv("DATABASE_NAME"),
                                      os.getenv("DATABASE_CLIENT_ID"),
                                      os.getenv("DATABASE_CLIENT_SECRET"))

    results = run_execute_plan_query(engine, os.getenv("SCHEMA_QUERY"))

    return {'is_draft_query_valid': results['success'], 'reason_for_draft_revision': results['error']}
