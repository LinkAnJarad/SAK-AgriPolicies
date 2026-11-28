import requests
import os
from dotenv import load_dotenv

load_dotenv()

DECISIONS_API_BASE_URL = os.getenv("DECISIONS_API_BASE_URL").rstrip("/")
DECISIONS_MODEL_NAME = os.getenv("DECISIONS_MODEL_NAME")
DECISIONS_API_KEY = os.getenv("DECISIONS_API_KEY")

_session = requests.Session()
_session.headers["Authorization"] = f"Bearer {DECISIONS_API_KEY}"

payload = {
    "model": DECISIONS_MODEL_NAME,
    "input": "Mochi is curled up in a sunny spot, purring softly and kneading a blanket. Her ears are relaxed and her eyes are half closed.",
    "questions": [
        {
            "type": "predicate",
            "instructions": "Mochi the cat is relaxed and comfortable."
        }
    ]
}
results = _session.post(f"{DECISIONS_API_BASE_URL}/decisions", json=payload, timeout=120)

print(results.json())



    