from pydantic import BaseModel


class UserOut(BaseModel):# Define el esquema de respuesta para la información de un usuario
    uid: str
    email: str
    display_name: str
    role: str
    photo_url: str | None = None
    created_at: int

    class Config:
        from_attributes = True  # permite crear esto directo desde el modelo SQLAlchemy