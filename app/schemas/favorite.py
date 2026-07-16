from pydantic import BaseModel


class FavoriteOut(BaseModel):# Define el esquema de respuesta para la información de un favorito
    user_id: str
    restaurant_id: str
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
    last_menu_photo_url: str | None
    last_menu_price: int | None
    added_at: int

    class Config:
        from_attributes = True