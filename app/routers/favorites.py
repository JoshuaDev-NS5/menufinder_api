from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.models.restaurant import Restaurant
from app.models.menu import MenuHistory
from app.models.favorite import FavoriteRestaurant
from app.schemas.favorite import FavoriteOut
from app.core.utils import current_timestamp_ms, current_date_str
from app.dependencies import get_current_user

router = APIRouter(prefix="/favorites", tags=["favorites"])


@router.get("", response_model=list[FavoriteOut])
def list_favorites(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return db.query(FavoriteRestaurant).filter(FavoriteRestaurant.user_id == current_user.uid).all()
#funcion para listar todos los restaurantes favoritos del usuario actual, recibe el usuario actual y una sesión de base de datos, devuelve una lista de objetos FavoriteOut

@router.post("/{restaurant_id}", response_model=FavoriteOut, status_code=status.HTTP_201_CREATED)
def add_favorite(
    restaurant_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    existing = (
        db.query(FavoriteRestaurant)
        .filter(
            FavoriteRestaurant.user_id == current_user.uid,
            FavoriteRestaurant.restaurant_id == restaurant_id,
        )
        .first()
    )
    if existing:
        return existing

    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurante no encontrado")

    today = current_date_str()
    today_menu = (
        db.query(MenuHistory)
        .filter(MenuHistory.restaurant_id == restaurant_id, MenuHistory.date == today)
        .first()
    )

    favorite = FavoriteRestaurant(
        user_id=current_user.uid,
        restaurant_id=restaurant.id,
        name=restaurant.name,
        address=restaurant.address,
        lat=restaurant.lat,
        lng=restaurant.lng,
        phone=restaurant.phone,
        open_time=restaurant.open_time,
        close_time=restaurant.close_time,
        is_verified=restaurant.is_verified,
        total_ratings=restaurant.total_ratings,
        average_score=restaurant.average_score,
        last_menu_photo_url=today_menu.photo_url if today_menu else None,
        last_menu_price=today_menu.price if today_menu else None,
        added_at=current_timestamp_ms(),
    )
    db.add(favorite)
    db.commit()
    db.refresh(favorite)
    return favorite
#funcion para agregar un restaurante a los favoritos del usuario actual, recibe el ID del restaurante, el usuario actual y una sesión de base de datos, verifica si el restaurante ya está en favoritos o si existe, luego crea un nuevo registro de favorito con la información del restaurante y del menú del día (si existe), finalmente devuelve un objeto FavoriteOut

@router.delete("/{restaurant_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_favorite(
    restaurant_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    favorite = (
        db.query(FavoriteRestaurant)
        .filter(
            FavoriteRestaurant.user_id == current_user.uid,
            FavoriteRestaurant.restaurant_id == restaurant_id,
        )
        .first()
    )
    if not favorite:
        raise HTTPException(status_code=404, detail="No tienes este restaurante en favoritos")

    db.delete(favorite)
    db.commit()
#funcion para eliminar un restaurante de los favoritos del usuario actual, recibe el ID del restaurante, el usuario actual y una sesión de base de datos, verifica si el restaurante está en favoritos y lo elimina, lanza una excepción si no se encuentra el restaurante en favoritos