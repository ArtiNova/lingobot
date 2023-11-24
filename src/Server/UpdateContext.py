from pydantic import BaseModel

class UpdateContext(BaseModel):
    username : str
    title : str
    context : list[dict]