from pydantic import BaseModel

class AudioRequest(BaseModel):
    message : str