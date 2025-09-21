import os

from langgraph.config import get_stream_writer

from ..agent_state import AgentState
from ..utils.mysql_util import execute_query
from ..utils.constants import Constants


def execute(state: AgentState) -> dict:
    writer = get_stream_writer()
    writer({Constants.STATE_PROGRESS_UPDATE_KEY: "Executing SQL query..."})
    print("Executing query with state:", state['sql_query_draft'])

    results = execute_query(state['sql_query_draft'])
    writer({Constants.STATE_PROGRESS_UPDATE_KEY: "SQL query execution complete."})
    return {'final_result': results, 'current_draft_revision': 0}
