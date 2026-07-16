from sqlalchemy import Column, String, Float, Boolean, Integer
from app.db.database import Base
#modelo de la tabla restaurants, que representa a los restaurantes de la aplicación
class Restaurant(Base):
    __tablename__ = "restaurants"

    id = Column(String, primary_key=True)
    owner_id = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    phone = Column(String, nullable=True)
    open_time = Column(String, nullable=True)
    close_time = Column(String, nullable=True)
    is_verified = Column(Boolean, nullable=False, default=False)
    total_ratings = Column(Integer, nullable=False, default=0)
    average_score = Column(Float, nullable=False, default=0.0)
    is_active = Column(Boolean, nullable=False, default=True)