from token_passing import AllReq

class UpdateTitle(AllReq):
    username: str
    oldTitle : str
    newTitle : str