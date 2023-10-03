from pydantic import BaseModel

class Request(BaseModel):
    input : str
    context : str

class Response(BaseModel):
    result_english : str
    result_hindi : str
