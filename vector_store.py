import json
import os
import shutil

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings


def create_vector_store(table_columns: dict):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    collection_name = "sql-schemas"
    persist_directory = f"./vector_stores/{collection_name}"

    # Delete the collection if it already exists
    if os.path.exists(persist_directory):
        shutil.rmtree(persist_directory)
        print(f"Deleted persisted directory: {persist_directory}")

    documents = []
    for table_name, columns in table_columns.items():
        # Convert each column dictionary to a json string for embedding
        json_columns = json.dumps(columns)
        document = Document(
            page_content=json_columns,
            metadata={"table_name": table_name}
        )
        documents.append(document)

    # Create a Chroma vector store for each table
    vector_store = Chroma.from_documents(
        persist_directory=persist_directory,
        collection_name=collection_name,
        embedding=embeddings,
        documents=documents,
    )

    docs_and_scores = vector_store.similarity_search_with_score(
        query="fetch all the agreements with end date greater than jan 2025", k=4)
    for doc, score in docs_and_scores:
        print(f"Found document: {doc.page_content} with score: {score} and metadata: {doc.metadata}")
