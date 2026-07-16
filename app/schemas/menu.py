from pydantic import BaseModel


class MenuCreate(BaseModel):# Define el esquema de solicitud para crear un nuevo menú
    date: str  # "yyyy-MM-dd"
    description: str
    price: int  # centavos
    options: list[str] = []
    is_available: bool = True
    is_last_plates: bool = False
    # photo_url NO va aquí: se sube por separado a R2 y se obtiene la URL


class MenuUpdate(BaseModel):# Define el esquema de solicitud para actualizar un menú existente
    description: str | None = None
    price: int | None = None
    options: list[str] | None = None
    is_available: bool | None = None
    is_last_plates: bool | None = None
    photo_url: str | None = None


class MenuOut(BaseModel):# Define el esquema de respuesta para la información de un menú
    id: str
    restaurant_id: str
    date: str
    photo_url: str
    description: str
    price: int
    options: list[str]
    is_available: bool
    is_last_plates: bool
    uploaded_at: int
    buenazos: int
    fatals: int

    class Config:
        from_attributes = True