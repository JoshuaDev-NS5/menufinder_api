from pydantic import BaseModel
from typing import Literal


class VoteCreate(BaseModel):# Define el esquema de solicitud para crear un nuevo voto
    menu_id: str
    restaurant_id: str
    vote_type: Literal["BUENAZO", "FATAL"]
    comment: str | None = None

# Define el esquema de respuesta para la información de un voto
class VoteOut(BaseModel):
    id: str
    user_id: str
    restaurant_id: str
    date: str
    vote_type: str
    comment: str | None
    timestamp: int

    class Config:
        from_attributes = True