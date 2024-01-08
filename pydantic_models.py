from pydantic import BaseModel

class TodoCreate(BaseModel):
    title: str
    description: str