from pydantic import BaseModel

class nameTitleRequest(BaseModel):
    question : list[dict]