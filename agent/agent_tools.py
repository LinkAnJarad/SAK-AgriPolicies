from langchain_chroma import Chroma
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document
from langchain_core.tools import tool
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

import pickle
import os
from dotenv import load_dotenv

load_dotenv()

with open("doc_cache/docs.pkl", 'rb') as doc_cache_file:
    docs = pickle.load(doc_cache_file)

embeddings = OpenAIEmbeddings(
    model=os.getenv("EMBEDDINGS_MODEL_NAME"),
    openai_api_base=os.getenv("EMBEDDINGS_API_BASE_URL"),
    openai_api_key=os.getenv("EMBEDDINGS_API_KEY"),
    check_embedding_ctx_length=False
)

vector_store = Chroma(
    embedding_function = embeddings,
    persist_directory = "./chroma_agripolicy_kb",
    collection_name = "agripolicy_kb"
)

bm25_retriever = BM25Retriever.from_documents(docs)
bm25_retriever.k = 10 # move to config.py

@tool
def lexical_retrieve(query: str, limit: int):
    """
    Retrieve documents chunks via lexical search.
    Params:
        query: str
        limit: int (max 10)
    """
    results = bm25_retriever.invoke(query)[:limit]

    formatted_result = ""

    for r in results:
        formatted_result += f"Title: {r.metadata["title"]}\n"
        formatted_result += f"Source document: {r.metadata["source_file"]}\n"
        formatted_result += f"Chunk content: {r.page_content}\n\n---\n\n"

    return formatted_result

@tool
def semantic_retrieve(query: str, limit: int):
    """
    Retrieve document chunks via semantic search.
    Params:
        query: str
        limit: int (max 10)
    """
    results = vector_store.similarity_search_with_score(query, k=limit)

    formatted_result = ""

    for r, score in results:
        formatted_result += f"Title: {r.metadata["title"]}\n"
        formatted_result += f"Source document: {r.metadata["source_file"]}\n"
        formatted_result += f"Chunk content: {r.page_content}\n\n---\n\n"

    return formatted_result

@tool
def read_document(document_name: str, line_range: list[int] = [0, 25]):
    """
    Read a document given filename and a range of lines.

    Params:
        document_name: str 
        line_range: list[int] of len 2. E.g. Lines 0 to 25: [0, 25]
    """
    with open(f"documents_md/{document_name}", "r", encoding="utf-8") as f:
        content = ""
        for i, line in enumerate(f):
            if ((i >= line_range[0]) and (i <= line_range[1])):
                content += f"{line}\n"
    
    return content

