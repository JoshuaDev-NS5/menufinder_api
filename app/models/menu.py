from sqlalchemy import Column, String, Integer, Boolean, BigInteger
from sqlalchemy.dialects.postgresql import ARRAY
from app.db.database import Base


class MenuHistory(Base):
    __tablename__ = "menu_history"#Nombre de la tabla en la base de datos

    id = Column(String, primary_key=True)
    restaurant_id = Column(String, nullable=False, index=True)
    date = Column(String, nullable=False)  # "yyyy-MM-dd"
    photo_url = Column(String, nullable=False)
    description = Column(String, nullable=False)
    price = Column(Integer, nullable=False)  # centavos
    options = Column(ARRAY(String), nullable=False, default=list)
    is_available = Column(Boolean, nullable=False, default=True)
    is_last_plates = Column(Boolean, nullable=False, default=False)
    uploaded_at = Column(BigInteger, nullable=False)
    buenazos = Column(Integer, nullable=False, default=0)
    fatals = Column(Integer, nullable=False, default=0)
    usuario_id = Column(String, nullable=False)  # dueño que lo subió