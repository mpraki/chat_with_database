from langchain.output_parsers import ResponseSchema
from langchain.output_parsers import StructuredOutputParser
from langchain_core.prompts import ChatPromptTemplate

from ..agent_state import AgentState
from ..llm import model
from ..prompts import SQL_VALIDATION_PROMPT


def analyze(state: AgentState) -> dict:
    print(f"Analysing drafted SQL query: {state['sql_query_draft']}")

    parser = StructuredOutputParser.from_response_schemas(response_schemas())
    format_instructions = parser.get_format_instructions(only_json=True)

    prompt_template = ChatPromptTemplate.from_template(template=SQL_VALIDATION_PROMPT)

    prompt = prompt_template.format_messages(format_instructions=format_instructions,
                                             sql_query=state['sql_query_draft'])
    print(f"Formatted prompt: {prompt}")

    response = model().invoke(prompt)
    json_output = parser.parse(response.content)

    return {'is_draft_query_valid': json_output.get('is_sql_valid'),
            'reason_for_draft_revision': json_output.get('reason_for_revision')}


def response_schemas():
    is_sql_valid = ResponseSchema(name="is_sql_valid", description="If the query is valid, set to True. "
                                                                   "If there are errors or improvements or best practices can be made to the query, set to False.",
                                  type="bool")
    reason_for_revision = ResponseSchema(name="reason_for_revision",
                                         description="If there are errors or improvements or best practices can be made to the query, provide the reason.",
                                         type="str")
    return [is_sql_valid, reason_for_revision]
