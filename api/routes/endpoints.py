from fastapi import APIRouter, HTTPException
from api.session_store import get_agent_from_session
from api import schemas
from langchain_core.messages import ToolMessage
import json
from agent.agent_tools import rerank
from api.response_utils import estimate_hallucination

router = APIRouter(
    prefix = "/sak-agripolicies"
)


def rerank_and_filter_provenance(query, messages, limit=10):
    provenance_list = []

    for msg in messages:
        if isinstance(msg, ToolMessage):
            content = json.loads(msg.content)
            for r in content:
                provenance_list.append(r)

    if len(provenance_list) == 0:
        return []

    reranked_list = rerank(query, [d["chunk_content"] for d in provenance_list])
    sorted_provenance_indices = list(range(len(provenance_list)))
    sorted_provenance_indices = [i for i, d in sorted(zip(sorted_provenance_indices, reranked_list), key=lambda pair: pair[1][1], reverse=True)]


    reranked_provenance = [(provenance_list[i], reranked_list[i][1]) for i in sorted_provenance_indices]

    seen_chunks = [] # replace with chunk_id
    dedup_provenance_ranked = []

    for d, score in reranked_provenance:
        if d["chunk_content"] not in seen_chunks:
            seen_chunks.append(d["chunk_content"])
            dedup_provenance_ranked.append((d, score))

    return dedup_provenance_ranked[:limit]

@router.post("/")
def send_message(message: schemas.UserMessage):

    agent = get_agent_from_session(message.session_id)
    messages = agent.call_agent(message.message)

    reranked_filtered_provenance = rerank_and_filter_provenance(message.message, messages)
    provenance_list = []
    for d, score in reranked_filtered_provenance:
        provenance_list.append(
            {
                "title": d["title"],
                "source_document": d["source_document"],
                "chunk_content": d["chunk_content"],
                "score": score
            }
        )

    hallucination_estimate = estimate_hallucination(message.message, messages[-1].content, provenance_list)

    response = {
        "message": messages[-1].content,
        "provenance": provenance_list,
        "hallucination_estimate": hallucination_estimate
    }

    return response