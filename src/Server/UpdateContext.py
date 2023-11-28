from token_passing import AllReq

class UpdateContext(AllReq):
    username : str
    title : str
    context : list[dict]