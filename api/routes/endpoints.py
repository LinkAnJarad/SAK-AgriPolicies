from fastapi import APIRouter, HTTPException
from api import schemas
from api.session_store import get_agent_from_session

router = APIRouter(
    prefix = "/sak-agripolicies"
)

@router.post("/", response_model=schemas.AIMessage)
def send_message(message: schemas.UserMessage):

    agent = get_agent_from_session(message.session_id)
    messages = agent.call_agent(message.message)
    return schemas.AIMessage(
        message = messages[-1].content
    )