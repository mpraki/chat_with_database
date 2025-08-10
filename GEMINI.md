# Project Overview

This project is a "Chat with your database" application that allows users to query a database using natural language. It is composed of two main components: a `schema_extractor` and a `data_extractor`.

The `schema_extractor` is a Python application that extracts database schema information from an Azure SQL database. It then uses a large language model (LLM) to generate descriptive explanations for each column in the schema. Finally, it stores the enriched schema information in a ChromaDB vector store. This allows for semantic search capabilities on the database schema, making it easier to understand and query the database.

The `data_extractor` is a data extraction agent that allows users to query a database using natural language. The agent uses a large language model (LLM) to understand the user's query and convert it into a SQL query. The SQL query is then executed against the database, and the results are displayed to the user in a Streamlit web interface.

## Architecture

The overall architecture is as follows:

1.  **Schema Extraction and Enrichment:** The `schema_extractor` connects to an Azure SQL database, extracts the schema, generates column descriptions using an LLM, and stores the result in a ChromaDB vector store.
2.  **Natural Language Querying:** The `data_extractor` provides a Streamlit web interface for users to enter natural language queries.
3.  **Query Understanding and SQL Generation:** The `data_extractor` uses the enriched schema from the vector store to understand the user's query and the database structure. It then uses LangChain and LangGraph to create a plan and generate a SQL query.
4.  **Query Execution and Results Display:** The generated SQL query is executed against the Azure SQL database, and the results are displayed to the user in the Streamlit interface.

## Key Technologies

*   **Python:** The main programming language for both components.
*   **LangChain:** A framework for developing applications powered by language models.
*   **LangGraph:** A library for building stateful, multi-actor applications with LLMs.
*   **Streamlit:** A framework for building the interactive web application.
*   **Azure SQL:** The target database for schema extraction and query execution.
*   **ChromaDB:** The vector store for storing the enriched schema information.
*   **Google Generative AI:** The LLM provider for generating column descriptions.

# Building and Running

This project consists of two separate applications that need to be run independently.

### 1. Schema Extractor

The `schema_extractor` needs to be run first to populate the vector store with the database schema information.

**a. Install Dependencies:**

```bash
cd schema_extractor
uv pip install -r requirements.txt
```
*(Note: A `requirements.txt` file is not present, but the dependencies are listed in the `pyproject.toml` and `uv.lock` files. You may need to generate a `requirements.txt` file from these files.)*

**b. Set Up Environment Variables:**

Create a `.env` and `.env.sql` file in the `schema_extractor` directory and add the necessary variables as described in `schema_extractor/GEMINI.md`.

**c. Run the Application:**

```bash
cd schema_extractor
python main.py
```

### 2. Data Extractor

Once the schema is extracted and stored in the vector store, you can run the `data_extractor` to interact with the database.

**a. Install Dependencies:**

```bash
cd data_extractor
pip install -r requirements.txt
```

**b. Run the Application:**

```bash
cd data_extractor
streamlit run ui.py
```

# Development Conventions

The project follows the standard Python coding conventions as defined by PEP 8. All code should be formatted using a code formatter such as Black or Ruff.

All new features should be developed in a separate branch and submitted as a pull request. All pull requests should be reviewed by at least one other developer before being merged into the main branch.
