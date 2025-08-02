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

    engine = pyodbc.connect(conn_str)
    return engine


def execute_query(engine, query):
    cursor = engine.cursor()
    cursor.execute(query)
    columns = [column[0] for column in cursor.description]
    results = [dict(zip(columns, row)) for row in cursor.fetchall()]
    cursor.close()
    return results
