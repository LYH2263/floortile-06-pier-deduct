from pydantic import BaseModel


class PierCreate(BaseModel):
    name: str = ""
    length: float
    width: float
