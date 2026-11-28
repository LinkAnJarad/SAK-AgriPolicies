from agent.agent import Agent
import pickle as pkl
from langchain_core.messages import ToolMessage, AIMessage
import json
import requests

# agent = Agent()

prompt = """Hello! Are there any PH policies for modernizing fisheries through research?"""
# messages = agent.call_agent(prompt)

# print(messages)

# with open('msg.pkl', 'wb') as f:
#     pkl.dump(messages, f)

# for i in messages:
#     print("--------------")
#     print(i.content)

# with open('msg.pkl', 'rb') as f:
#     messages = pkl.load(f)

# from agent.agent_tools import rerank

# provenance_list = []

# for msg in messages:
#     if isinstance(msg, ToolMessage):
#         content = json.loads(msg.content)
#         for r in content:
#             provenance_list.append(r)

# reranked_list = rerank(prompt, [d["chunk_content"] for d in provenance_list])
# sorted_provenance_indices = list(range(len(provenance_list)))
# sorted_provenance_indices = [i for i, d in sorted(zip(sorted_provenance_indices, reranked_list), key=lambda pair: pair[1][1], reverse=True)]


# reranked_provenance = [(provenance_list[i], reranked_list[i][1]) for i in sorted_provenance_indices]

# seen_chunks = [] # replace with chunk_id
# dedup_provenance_ranked = []

# for d, score in reranked_provenance:
#     if d["chunk_content"] not in seen_chunks:
#         seen_chunks.append(d["chunk_content"])
#         dedup_provenance_ranked.append((d, score))

# print(len(reranked_provenance))
# print(len(dedup_provenance_ranked))

# print(dedup_provenance_ranked[:5])
# # print(len([m for m in messages if isinstance(m, ToolMessage)]))





{
  "model": "gpt-6-luna",
  "input": "Mochi is curled up in a sunny spot, purring softly and kneading a blanket. Her ears are relaxed and her eyes are half closed.",
  "questions": [
    {
      "type": "predicate",
      "instructions": "Mochi the cat is relaxed and comfortable."
    }
  ]
}