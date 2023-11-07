from pydantic import BaseModel

class correctGrammarRequest(BaseModel):
    text : str