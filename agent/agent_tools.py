from langchain_chroma import Chroma
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document
from langchain_core.tools import tool
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

import pickle
import os
from dotenv import load_dotenv
import requests

load_dotenv()

with open("doc_cache/docs.pkl", 'rb') as doc_cache_file:
    docs = pickle.load(doc_cache_file)

# -------------------------------------------
embeddings = OpenAIEmbeddings(
    model=os.getenv("EMBEDDINGS_MODEL_NAME"),
    openai_api_base=os.getenv("EMBEDDINGS_API_BASE_URL"),
    openai_api_key=os.getenv("EMBEDDINGS_API_KEY"),
    check_embedding_ctx_length=False
)
# -------------------------------------------
vector_store = Chroma(
    embedding_function = embeddings,
    persist_directory = "./chroma_agripolicy_kb",
    collection_name = "agripolicy_kb"
)
# -------------------------------------------
RERANKER_API_BASE_URL = os.getenv("RERANKER_API_BASE_URL").rstrip("/")
RERANKER_MODEL_NAME = os.getenv("RERANKER_MODEL_NAME")
RERANKER_API_KEY = os.getenv("RERANKER_API_KEY")

_session = requests.Session()
_session.headers["Authorization"] = f"Bearer {RERANKER_API_KEY}"

# -------------------------------------------

bm25_retriever = BM25Retriever.from_documents(docs)
bm25_retriever.k = 10 # move to config.py

# -------------------------------------------


def rerank(query: str, documents: list[str], timeout=120):
    payload = {"model": RERANKER_MODEL_NAME, "query": query, "documents": documents}
    result = _session.post(f"{RERANKER_API_BASE_URL}/rerank", json=payload, timeout=timeout)
    result = result.json()
    result_dict = {d["index"]: d["relevance_score"] for d in result["results"]}

    reranked = []
    for i in range(len(documents)):
        doc = documents[i]
        score = result_dict[i]
        reranked.append((doc, score))

    return reranked


# -------------------------------------------

def lexical_retrieve(query: str, limit: int):
    results = bm25_retriever.invoke(query)[:limit]
    return results

@tool
def lexical_retrieve_tool(query: str, limit: int):
    """
    Retrieve documents chunks via lexical search.
    Params:
        query: str
        limit: int (max 10)
    """

    if limit > 10:
        return "Maximum limit is 10"

    results_lexical = lexical_retrieve(query, limit)

    results = []

    for r in results_lexical:

        results.append({
            "title": r.metadata["title"],
            "source_document": r.metadata["source_file"],
            "chunk_content": r.page_content
        })

    return results

def semantic_retrieve(query: str, limit: int):
    results = vector_store.similarity_search_with_score(query, k=10) # max k first, then slice to limit
    
    results_for_reranking = [r.page_content for r, _ in results]
    reranked_results = rerank(query, results_for_reranking)

    results_all_scores = []
    for i, (r, semantic_score) in enumerate(results[:limit]):
        _, reranked_score = reranked_results[i]
        results_all_scores.append(
            (r, 1-round(semantic_score, 2), round(reranked_score, 2)) # 1 - semantic score since lower = better
        )

    results_all_scores = sorted(results_all_scores, key=lambda x: x[-1], reverse=True)
    return results_all_scores

@tool
def semantic_retrieve_tool(query: str, limit: int):
    """
    Retrieve document chunks via semantic search.
    Params:
        query: str
        limit: int (max 10)
    """

    if limit > 10:
        return "Maximum limit is 10"

    results_all_scores = semantic_retrieve(query, limit)

    formatted_result = ""

    results = []

    for r, semantic_score, reranked_score in results_all_scores:
        results.append({
            "title": r.metadata["title"],
            "source_document": r.metadata["source_file"],
            "semantic_score": semantic_score,
            "reranked_score": reranked_score,
            "chunk_content": r.page_content,
        })

    return results

@tool
def read_document_tool(document_name: str, line_range: list[int] = [0, 25]):
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
    
    result = {
        "source_document": document_name,
        "chunk_content": content
    }
    return result

if __name__ == "__main__":
    r = lexical_retrieve("Philippine agricultural fisheries and laws", 2)
    print(r)