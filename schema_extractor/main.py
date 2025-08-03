import os
import time

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate

from azure_sql_util import get_azure_sql_connection, execute_query
from llm import model as llm_model
from prompts import SCHEMA_DESCRIPTION
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

    prompt_template = ChatPromptTemplate.from_template(SCHEMA_DESCRIPTION)

    updated_table_dict = {}
    model = llm_model()
    # iterate over the table_dict and print the table names and their columns
    for table_name, columns in table_dict.items():
        prompt = prompt_template.invoke({"data_structure": columns})
        # print(f"final prompt: {prompt}\n")
        updated_columns = model.invoke(prompt)
        updated_table_dict[table_name] = updated_columns.content
        # sleep for 5 seconds to avoid rate limiting
        time.sleep(5)

    print(f"updated_table_dict : {updated_table_dict}\n")

    # Create vector store
    create_vector_store(updated_table_dict)


if __name__ == "__main__":
    main()
