import os
import sqlite3

from dotenv import load_dotenv
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.errors import GraphRecursionError
from langgraph.graph import StateGraph
from pyodbc import ProgrammingError

from .agent_state import AgentState
from .nodes import planner_llm, dry_run_executor
from .nodes import sql_query_analyzer_llm
from .nodes import sql_query_drafter_llm
from .nodes import sql_query_executor
from .nodes import user_query_analyzer_llm
from .nodes import vector_search
from .nodes.validators import sql_query_validator
from .nodes.validators import vector_score_validator
from .utils.constants import Constants


class Agent:

    def __init__(self, checkpointer):
        load_dotenv()

        graph_builder = StateGraph(AgentState)
        graph_builder.add_node('vector_search', vector_search.search)
        graph_builder.add_node('user_query_analyzer', user_query_analyzer_llm.analyze)
        graph_builder.add_node('planner', planner_llm.plan)
        graph_builder.add_node('drafter', sql_query_drafter_llm.draft)
        graph_builder.add_node('reviewer', sql_query_analyzer_llm.analyze)
        graph_builder.add_node('dry_run_executor', dry_run_executor.execute)
        graph_builder.add_node('sql_query_executor', sql_query_executor.execute)

        graph_builder.add_conditional_edges('vector_search', vector_score_validator.validate,
                                            {True: 'planner', False: 'user_query_analyzer'})
        graph_builder.add_conditional_edges('reviewer', sql_query_validator.validate,
                                            {True: 'dry_run_executor', False: 'drafter'})
        graph_builder.add_conditional_edges('dry_run_executor', sql_query_validator.validate,
                                            {True: 'sql_query_executor', False: 'drafter'})

        graph_builder.set_entry_point('vector_search')
        graph_builder.add_edge('user_query_analyzer', 'vector_search')
        graph_builder.add_edge('planner', 'drafter')
        graph_builder.add_edge('drafter', 'reviewer')
        graph_builder.set_finish_point('sql_query_executor')

        self.graph = graph_builder.compile(checkpointer=checkpointer, interrupt_after=["user_query_analyzer"])


def run_agent(task: str, session_id: str) -> str:
    sqlite_saver = create_memory_db(session_id)
    agent = Agent(sqlite_saver)

    # draw(agent)

    config = {"configurable": {"thread_id": "1"}, "recursion_limit": Constants.RECURSION_LIMIT}
    agent.graph.invoke({'task': task}, config=config)
    return agent.graph.get_state(config).values['user_query_clarification']


def stream_agent(task: str, session_id: str):
    sqlite_saver = create_memory_db(session_id)
    agent = Agent(sqlite_saver)

    # draw(agent)

    config = {"configurable": {"thread_id": "1"}, "recursion_limit": Constants.RECURSION_LIMIT}
    try:
        for chunk in agent.graph.stream({'task': task}, config=config, stream_mode=["custom", "values"]):
            data = chunk[-1]
            if Constants.STATE_PROGRESS_UPDATE_KEY in data:
                yield {"type": "progress", "content": data[Constants.STATE_PROGRESS_UPDATE_KEY]}
            if "user_query_clarification" in data:
                yield {"type": "response", "content": data["user_query_clarification"]}
            if "final_result" in data:
                final_result_ = data["final_result"]
                yield {"type": "response", "content": "No results found!" if len(final_result_) == 0 else final_result_}
    except GraphRecursionError as e:
        print(f"{e}")
        yield {"type": "error", "content": "Your maximum conversation limit reached!"}
    except ProgrammingError as e:
        print(f"{e}")
        yield {"type": "error", "content": "Something went wrong! Please try again!!"}


def create_memory_db(session_id: str) -> SqliteSaver:
    db_dir = "../memory"
    db_path = os.path.join(db_dir, session_id + "conversation_history.db")
    os.makedirs(db_dir, exist_ok=True)
    conn = sqlite3.connect(db_path, check_same_thread=False)
    return SqliteSaver(conn)


def draw(agent):
    print("--- LangGraph Diagram ---")
    try:
        with open("langgraph_diagram.png", "wb") as f:
            f.write(agent.graph.get_graph().draw_mermaid_png())
        print("Saved LangGraph diagram to langgraph_diagram.png")
    except Exception as e:
        print(f"Could not save LangGraph diagram: {e}")
    print("-------------------------")
