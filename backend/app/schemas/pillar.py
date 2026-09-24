from pydantic import BaseModel


class PillarIn(BaseModel):
    length: float
    width: float
