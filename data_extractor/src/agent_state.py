from typing import TypedDict


class AgentState(TypedDict, total=False):
    task: str
    final_result: str
