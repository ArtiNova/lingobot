from pydantic import BaseModel

class conversationRequest(BaseModel):
    username : str

class conversationResponse(BaseModel):
    titles : list