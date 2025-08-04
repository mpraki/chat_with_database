from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import StateGraph, END

from .agent_state import AgentState
from .nodes import planner_llm, dry_run_executor
from .nodes import sql_query_analyzer_llm
from .nodes import sql_query_drafter_llm
from .nodes import sql_query_executor
from .nodes import user_query_analyzer_llm
from .nodes import vector_search
from .nodes.validators import user_query_validator, sql_query_validator, dry_run_validator
from .nodes.validators import vector_score_validator


class Agent:

    def __init__(self, checkpointer=None):
        graph_builder = StateGraph(AgentState)
        graph_builder.add_node('vector_search', vector_search.search)
        graph_builder.add_node('user_query_analyzer', user_query_analyzer_llm.analyze)
        graph_builder.add_node('planner', planner_llm.plan)
        graph_builder.add_node('drafter', sql_query_drafter_llm.draft)
        graph_builder.add_node('sql_query_analyzer', sql_query_analyzer_llm.analyze)
        graph_builder.add_node('dry_run_executor', dry_run_executor.execute)
        graph_builder.add_node('sql_query_executor', sql_query_executor.execute)

        graph_builder.add_conditional_edges('vector_search', vector_score_validator.validate,
                                         {True: 'planner', False: 'user_query_analyzer'})
        # graph_builder.add_conditional_edges('user_query_analyzer', user_query_validator.validate,
        #                                  {True: END, False: 'planner'})
        graph_builder.add_conditional_edges('sql_query_analyzer', sql_query_validator.validate,
                                         {True: 'dry_run_executor', False: 'drafter'})
        graph_builder.add_conditional_edges('dry_run_executor', dry_run_validator.validate,
                                         {True: 'sql_query_executor', False: 'drafter'})

        graph_builder.set_entry_point('vector_search')
        graph_builder.add_edge('user_query_analyzer', 'vector_search')
        graph_builder.add_edge('planner', 'drafter')
        graph_builder.add_edge('drafter', 'sql_query_analyzer')
        graph_builder.set_finish_point('sql_query_analyzer')

        self.graph = graph_builder.compile(checkpointer=checkpointer, interrupt_before=["user_query_analyzer"])


def run_agent(task: str) -> str:
    with SqliteSaver.from_conn_string(":memory:") as memory:
        agent = Agent(checkpointer=memory)

        print("--- LangGraph Diagram ---")
        try:
            # This requires playwright to be installed and a browser to be available
            # pip install playwright
            # playwright install
            with open("langgraph_diagram.png", "wb") as f:
                f.write(agent.graph.get_graph().draw_mermaid_png())
            print("Saved LangGraph diagram to langgraph_diagram.png")
        except Exception as e:
            print(f"Could not save LangGraph diagram: {e}")
        print("-------------------------")

        thread = {"configurable": {"thread_id": "1"}}
        agent.graph.invoke({'task': task}, config=thread)
        return agent.graph.get_state(thread)['final_result']

