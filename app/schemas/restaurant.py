from pydantic import BaseModel
    

class RestaurantCreate(BaseModel):# Define el esquema de solicitud para crear un nuevo restaurante
    name: str
    address: str
    lat: float
    lng: float
    phone: str | None = None
    open_time: str = "08:00"
    close_time: str = "18:00"


class RestaurantUpdate(BaseModel):# Define el esquema de solicitud para actualizar un restaurante existente
    name: str | None = None
    address: str | None = None
    lat: float | None = None
    lng: float | None = None
    phone: str | None = None
    open_time: str | None = None
    close_time: str | None = None
    is_active: bool | None = None


class RestaurantOut(BaseModel):# Define el esquema de respuesta para la información de un restaurante
    id: str
    owner_id: str
    name: str
    address: str
    lat: float
    lng: float
    phone: str | None
    open_time: str | None
    close_time: str | None
    is_verified: bool
    total_ratings: int
    average_score: float
    is_active: bool

    class Config:
        from_attributes = True