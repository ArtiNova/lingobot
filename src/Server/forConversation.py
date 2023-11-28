from token_passing import AllReq

class conversationRequest(AllReq):
    username : str

class conversationResponse(AllReq):
    titles : list