from token_passing import AllReq as BaseModel


class UpdateChatRequest(BaseModel):
    username : str
    title : str

class UpdateChatResponse(BaseModel):
    status : bool

class UpdateCurrentRequest(BaseModel):
    username : str
    title : str
    messages : list
