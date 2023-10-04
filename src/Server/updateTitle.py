from pydantic import BaseModel

class UpdateTitle(BaseModel):
    username: str
    oldTitle : str
    newTitle : str