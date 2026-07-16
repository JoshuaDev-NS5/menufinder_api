from sqlalchemy import Column, String, BigInteger
from app.db.database import Base

#modelo de la tabla users, que representa a los usuarios de la aplicación
class User(Base):
    __tablename__ = "users"

    uid = Column(String, primary_key=True)
    email = Column(String, unique=True, nullable=False, index=True)
    display_name = Column(String, nullable=False)
    password = Column(String, nullable=False)  # hash bcrypt, nunca texto plano
    role = Column(String, nullable=False)  # "DINER" | "OWNER"
    photo_url = Column(String, nullable=True)# la columna photo_url es opcional, puede ser nula
    created_at = Column(BigInteger, nullable=False)