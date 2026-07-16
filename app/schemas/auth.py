from pydantic import BaseModel, EmailStr
from typing import Literal


class RegisterRequest(BaseModel):# Define el esquema de solicitud para el registro de un nuevo usuario
    email: EmailStr
    password: str
    display_name: str
    role: Literal["DINER", "OWNER"]


class LoginRequest(BaseModel):# Define el esquema de solicitud para el inicio de sesión
    email: EmailStr
    password: str


class TokenResponse(BaseModel):# Define el esquema de respuesta para el token de acceso
    access_token: str
    token_type: str = "bearer"