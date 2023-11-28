from token_passing import AllReq

class PreviousRequest(AllReq):
    username : str
    title : str

class PreviousResponse(AllReq):
    messages : list