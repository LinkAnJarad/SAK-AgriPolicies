import requests
import os
from dotenv import load_dotenv

load_dotenv()

DECISIONS_API_BASE_URL = os.getenv("DECISIONS_API_BASE_URL").rstrip("/")
DECISIONS_MODEL_NAME = os.getenv("DECISIONS_MODEL_NAME")
DECISIONS_API_KEY = os.getenv("DECISIONS_API_KEY")

_session = requests.Session()
_session.headers["Authorization"] = f"Bearer {DECISIONS_API_KEY}"

def estimate_hallucination(user_message: str, ai_message: str, provenance_list):

    cleaned_provenance_list = []
    for d in provenance_list:
        cleaned_provenance_list.append(
            {
                "title": d["title"],
                "chunk_content": d["chunk_content"]
            }
        )
    
    decisions_input = {
        "user_message": user_message,
        "ai_message": ai_message,
        "chunk_contexts": cleaned_provenance_list
    }

    payload = {
        "model": DECISIONS_MODEL_NAME,
        "input": str(decisions_input),
        "questions": [
            {
                "type": "predicate",
                "instructions": f"The AI's message/response to the user is 100% accurately based and grounded in the chunk contexts. The chunk contexts helped guide the AI's message, and the AI did not hallucinate at all."
            }
        ]
    }

    results = _session.post(f"{DECISIONS_API_BASE_URL}/decisions", json=payload, timeout=120)
    results = results.json()

    hallucination_estimate = results["answers"][0]["probability"]
    return hallucination_estimate