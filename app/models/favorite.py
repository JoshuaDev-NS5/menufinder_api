from sqlalchemy import Column, String, Float, Boolean, Integer, BigInteger
from app.db.database import Base


class FavoriteRestaurant(Base):
    __tablename__ = "favorite_restaurants"

    # Llave compuesta: un usuario no puede tener el mismo restaurante 2 veces
    user_id = Column(String, primary_key=True)
    restaurant_id = Column(String, primary_key=True)

    # Datos "cacheados" del restaurante al momento de agregarlo a favoritos,
    # para no depender de un JOIN cada vez que se abre la pantalla de favoritos
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
    last_menu_photo_url = Column(String, nullable=True)
    last_menu_price = Column(Integer, nullable=True)
    added_at = Column(BigInteger, nullable=False)