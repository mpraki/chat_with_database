import os

import pyodbc


def get_azure_sql_connection(server, database, client_id, client_secret):
    conn_str = (
        f"DRIVER={{ODBC Driver 18 for SQL Server}};"
        f"SERVER={server};"
        f"DATABASE={database};"
        f"UID={client_id};"
        f"PWD={client_secret};"
        f"Authentication=ActiveDirectoryServicePrincipal;"
    )

    return pyodbc.connect(conn_str)


def engine():
    return get_azure_sql_connection(os.getenv("DATABASE_URL"),
                                    os.getenv("DATABASE_NAME"),
                                    os.getenv("DATABASE_CLIENT_ID"),
                                    os.getenv("DATABASE_CLIENT_SECRET"))


def run_execute_plan_query(query) -> dict:
    cursor = engine().cursor()
    try:
        cursor.execute("SET NOEXEC ON;")
        cursor.execute(query)
        # If no exception, the query is valid. No result set is produced with NOEXEC ON.
        return {"success": True, "data": None, "error": None}
    except Exception as e:
        print(f"Error executing query: {e}")
        return {"success": False, "data": None, "error": str(e)}
    finally:
        cursor.execute("SET NOEXEC OFF;")
        cursor.close()


def execute_query(query):
    print(f"Executing query: {query}")
    cursor = engine().cursor()
    cursor.execute(query)
    columns = [column[0] for column in cursor.description]
    results = [dict(zip(columns, row)) for row in cursor.fetchall()]
    cursor.close()
    return results
