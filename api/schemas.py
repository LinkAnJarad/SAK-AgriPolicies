from pydantic import BaseModel, Field

class UserMessage(BaseModel):
    message: str = Field(..., min_length=1)
    session_id: str = Field(..., min_length=1)

class AIMessage(BaseModel):
    message: str = Field(..., min_length=1)

