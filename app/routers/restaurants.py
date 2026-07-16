from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.models.restaurant import Restaurant
from app.models.menu import MenuHistory
from app.schemas.restaurant import RestaurantCreate, RestaurantUpdate, RestaurantOut
from app.core.utils import generate_id
from app.dependencies import require_owner

# Rutas de restaurantes
router = APIRouter(prefix="/restaurants", tags=["restaurants"])

# Rutas de restaurantes
@router.get("", response_model=list[RestaurantOut])
def list_restaurants(db: Session = Depends(get_db)):
    # Pantalla de inicio del comensal: trae todos los activos
    return db.query(Restaurant).filter(Restaurant.is_active == True).all()
#funcion para listar todos los restaurantes activos, recibe una sesión de base de datos y devuelve una lista de objetos RestaurantOut


#Ruta para obtener el restaurante del dueño actual
@router.get("/me", response_model=RestaurantOut)
def get_my_restaurant(
    current_user: User = Depends(require_owner),
    db: Session = Depends(get_db),
):
    restaurant = db.query(Restaurant).filter(Restaurant.owner_id == current_user.uid).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Aún no has creado tu restaurante")
    return restaurant
#funcion para obtener el restaurante del dueño actual, recibe el usuario actual y una sesión de base de datos, devuelve un objeto RestaurantOut o lanza una excepción si no se encuentra el restaurante

@router.get("/{restaurant_id}", response_model=RestaurantOut)
def get_restaurant(restaurant_id: str, db: Session = Depends(get_db)):
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurante no encontrado")
    return restaurant
#funcion para obtener un restaurante por su ID, recibe el ID del restaurante y una sesión de base de datos, devuelve un objeto RestaurantOut o lanza una excepción si no se encuentra el restaurante

@router.post("", response_model=RestaurantOut, status_code=status.HTTP_201_CREATED)
def create_restaurant(
    payload: RestaurantCreate,
    current_user: User = Depends(require_owner),
    db: Session = Depends(get_db),
):
    existing = db.query(Restaurant).filter(Restaurant.owner_id == current_user.uid).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Ya tienes un restaurante creado. Edítalo en vez de crear otro.",
        )

    restaurant = Restaurant(
        id=generate_id("rest_"),
        owner_id=current_user.uid,
        name=payload.name,
        address=payload.address,
        lat=payload.lat,
        lng=payload.lng,
        phone=payload.phone,
        open_time=payload.open_time,
        close_time=payload.close_time,
        is_verified=False,
        total_ratings=0,
        average_score=0.0,
        is_active=True,
    )
    db.add(restaurant)
    db.commit()
    db.refresh(restaurant)
    return restaurant
#funcion para crear un nuevo restaurante, recibe un payload de tipo RestaurantCreate, el usuario actual y una sesión de base de datos, devuelve un objeto RestaurantOut o lanza una excepción si el usuario ya tiene un restaurante creado


@router.put("/{restaurant_id}", response_model=RestaurantOut)
def update_restaurant(
    restaurant_id: str,
    payload: RestaurantUpdate,
    current_user: User = Depends(require_owner),
    db: Session = Depends(get_db),
):
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurante no encontrado")
    if restaurant.owner_id != current_user.uid:
        raise HTTPException(status_code=403, detail="No eres dueño de este restaurante")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(restaurant, field, value)

    db.commit()
    db.refresh(restaurant)
    return restaurant
#funcion para actualizar un restaurante existente, recibe el ID del restaurante, un payload de tipo RestaurantUpdate, el usuario actual y una sesión de base de datos, devuelve un objeto RestaurantOut o lanza una excepción si no se encuentra el restaurante o si el usuario no es el dueño del restaurante

@router.delete("/{restaurant_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_restaurant(
    restaurant_id: str,
    current_user: User = Depends(require_owner),
    db: Session = Depends(get_db),
):
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurante no encontrado")
    if restaurant.owner_id != current_user.uid:
        raise HTTPException(status_code=403, detail="No eres dueño de este restaurante")

    # Borrado en cascada manual: como el diagrama no define FKs formales,
    # SQLAlchemy no lo hace solo — hay que limpiar los menús a mano.
    db.query(MenuHistory).filter(MenuHistory.restaurant_id == restaurant_id).delete()
    db.delete(restaurant)
    db.commit()
#funcion para eliminar un restaurante existente, recibe el ID del restaurante, el usuario actual y una sesión de base de datos, lanza una excepción si no se encuentra el restaurante o si el usuario no es el dueño del restaurante, y elimina los menús asociados al restaurante antes de eliminar el restaurante mismo