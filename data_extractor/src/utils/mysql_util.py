import os
import pyodbc

def get_mysql_connection(host, port, database, user, password):
    conn_str = (
        f"DRIVER={{MariaDB ODBC 3.1 Driver}};"
        f"SERVER={host};"
        f"PORT={port};"
        f"DATABASE={database};"
        f"UID={user};"
        f"PWD={password};"
    )
    return pyodbc.connect(conn_str)

def engine():
    return get_mysql_connection(os.getenv("DATABASE_HOST"),
                                os.getenv("DATABASE_PORT"),
                                os.getenv("DATABASE_NAME"),
                                os.getenv("DATABASE_USER"),
                                os.getenv("DATABASE_PASSWORD"))

def run_execute_plan_query(query) -> dict:
    cursor = engine().cursor()
    try:
        cursor.execute(f"EXPLAIN {query}")
        columns = [column[0] for column in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return {"success": True, "data": results, "error": None}
    except Exception as e:
        print(f"Error executing query: {e}")
        return {"success": False, "data": None, "error": str(e)}
    finally:
        cursor.close()

def execute_query(query):
    print(f"Executing query: {query}")
    cursor = engine().cursor()
    cursor.execute(query)
    columns = [column[0] for column in cursor.description]
    results = [dict(zip(columns, row)) for row in cursor.fetchall()]
    cursor.close()
    return results
