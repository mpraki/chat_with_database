import os

from ..agent_state import AgentState
from ..utils.azure_sql_util import get_azure_sql_connection, execute_query


def execute(state: AgentState) -> dict:
    print("Executing query with state:", state)
    engine = get_azure_sql_connection(os.getenv("DATABASE_URL"),
                                      os.getenv("DATABASE_NAME"),
                                      os.getenv("DATABASE_CLIENT_ID"),
                                      os.getenv("DATABASE_CLIENT_SECRET"))

    results = execute_query(engine, os.getenv("SCHEMA_QUERY"))

    return {'final_result': results}
