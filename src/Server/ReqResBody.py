from token_passing import AllReq

class Request(AllReq):
    input : str
    context : list[dict]

class Response(AllReq):
    result_english : str
    result_hindi : str
