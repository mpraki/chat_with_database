import os

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate

from azure_sql_util import get_azure_sql_connection, execute_query
from llm import model as llm_model
from vector_store import create_vector_store


def main():
    print("Hello from chat-with-database!\n")

    load_dotenv()
    engine = get_azure_sql_connection(os.getenv("DATABASE_URL"),
                                      os.getenv("DATABASE_NAME"),
                                      os.getenv("DATABASE_CLIENT_ID"),
                                      os.getenv("DATABASE_CLIENT_SECRET"))

    load_dotenv(".env.sql")
    results = execute_query(engine, os.getenv("SCHEMA_QUERY"))
    table_dict = {}
    for row in results:
        table_name = row.get('TableName')
        if table_name not in table_dict:
            table_dict[table_name] = []
        table_dict[table_name].append(row)

    prompt_template = ChatPromptTemplate.from_template("""Parse the data structure and For each item in the data structure,
    add a "description" field with a concise explanation of the column's purpose (15-50 words)
    and return the updated list of items. Do not add any additional text. Return only the list of items in python dict type.
    Do not include any code block delimiters like ```python or ``` in your response.
     e.g.: [{{'TableName': 'employees', 'ColumnName': 'employee_id', 'DataType':
    'bigint', 'MaxLength': 8, 'IsNullable': False, 'CONSTRAINT_TYPE': 'PRIMARY_KEY_CONSTRAINT', 'ConstraintName':
    'employees_pk', 'ReferencedTable': None, 'ReferencedColumn': None, 'description': 'Unique identifier for each employee record.
    Serves as the primary key and is used to reference employees throughout the system.'}},
    {{'TableName': 'employees', 'ColumnName': 'department_id', 'DataType': 'bigint', 'MaxLength': 8, 'IsNullable': False,
    'CONSTRAINT_TYPE': 'FOREIGN KEY', 'ConstraintName': 'employees_department_id_fk', 'ReferencedTable': 'departments',
    'ReferencedColumn': 'department_id', 'description': 'References the department the employee belongs to.
    Ensures that each employee is linked to a valid department in the departments table.'}}] data_structure: {data_structure}""")

    updated_table_dict = {}
    # iterate over the table_dict and print the table names and their columns
    for table_name, columns in table_dict.items():
        prompt = prompt_template.invoke({"data_structure": columns})
        # print(f"final prompt: {prompt}\n")
        updated_columns = llm_model().invoke(prompt)
        updated_table_dict[table_name] = updated_columns.content

    print(f"updated_table_dict : {updated_table_dict}\n")

    # Create vector store
    create_vector_store(updated_table_dict)


if __name__ == "__main__":
    main()
