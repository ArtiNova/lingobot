from pydantic import BaseModel

class PreviousRequest(BaseModel):
    username : str
    title : str

class PreviousResponse(BaseModel):
    messages : list