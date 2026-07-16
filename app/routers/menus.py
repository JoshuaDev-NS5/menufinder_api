from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.models.restaurant import Restaurant
from app.models.menu import MenuHistory
from app.schemas.menu import MenuUpdate, MenuOut
from app.core.utils import generate_id, current_timestamp_ms, current_date_str
from app.dependencies import require_owner
from app.services.storage import upload_menu_photo, delete_menu_photo

router = APIRouter(tags=["menus"])


def _get_owned_restaurant(restaurant_id: str, current_user: User, db: Session) -> Restaurant:
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurante no encontrado")
    if restaurant.owner_id != current_user.uid:
        raise HTTPException(status_code=403, detail="No eres dueño de este restaurante")
    return restaurant
#funcion para obtener un restaurante por su ID y verificar que el usuario actual sea el dueño, recibe el ID del restaurante, el usuario actual y una sesión de base de datos, devuelve un objeto Restaurant o lanza una excepción si no se encuentra el restaurante o si el usuario no es el dueño del restaurante

@router.get("/restaurants/{restaurant_id}/menu/today", response_model=MenuOut)
def get_today_menu(restaurant_id: str, db: Session = Depends(get_db)):
    today = current_date_str()
    menu = (
        db.query(MenuHistory)
        .filter(MenuHistory.restaurant_id == restaurant_id, MenuHistory.date == today)
        .first()
    )
    if not menu:
        raise HTTPException(status_code=404, detail="Este restaurante no tiene menú hoy")
    return menu
#funcion para obtener el menú del día de un restaurante, recibe el ID del restaurante y una sesión de base de datos, devuelve un objeto MenuOut o lanza una excepción si no se encuentra el menú del día

@router.get("/restaurants/{restaurant_id}/menus", response_model=list[MenuOut])
def get_menu_history(restaurant_id: str, db: Session = Depends(get_db)):
    return (
        db.query(MenuHistory)
        .filter(MenuHistory.restaurant_id == restaurant_id)
        .order_by(MenuHistory.uploaded_at.desc())
        .all()
    )
#funcion para obtener el historial de menús de un restaurante, recibe el ID del restaurante y una sesión de base de datos, devuelve una lista de objetos MenuOut ordenados por fecha de subida en orden descendente

@router.post(
    "/restaurants/{restaurant_id}/menus",
    response_model=MenuOut,
    status_code=status.HTTP_201_CREATED,
)
async def upsert_today_menu(
    restaurant_id: str,
    description: str = Form(...),
    price: int = Form(...),
    options: str = Form(""),  # coma-separado desde el cliente: "Pollo,Pescado,Vegano"
    is_available: bool = Form(True),
    is_last_plates: bool = Form(False),
    photo: UploadFile = File(...),
    current_user: User = Depends(require_owner),
    db: Session = Depends(get_db),
):
    _get_owned_restaurant(restaurant_id, current_user, db)

    today = current_date_str()
    photo_url = await upload_menu_photo(photo, restaurant_id)
    options_list = [o.strip() for o in options.split(",") if o.strip()]

    existing = (
        db.query(MenuHistory)
        .filter(MenuHistory.restaurant_id == restaurant_id, MenuHistory.date == today)
        .first()
    )

    if existing:
        # Mismo criterio que tu docId compuesto restaurantId_fecha en Firestore:
        # un solo menú activo por día, se reemplaza si ya existe
        old_photo = existing.photo_url
        existing.photo_url = photo_url
        existing.description = description
        existing.price = price
        existing.options = options_list
        existing.is_available = is_available
        existing.is_last_plates = is_last_plates
        existing.uploaded_at = current_timestamp_ms()
        db.commit()
        db.refresh(existing)
        delete_menu_photo(old_photo)
        return existing

    menu = MenuHistory(
        id=generate_id("menu_"),
        restaurant_id=restaurant_id,
        date=today,
        photo_url=photo_url,
        description=description,
        price=price,
        options=options_list,
        is_available=is_available,
        is_last_plates=is_last_plates,
        uploaded_at=current_timestamp_ms(),
        buenazos=0,
        fatals=0,
        usuario_id=current_user.uid,
    )
    db.add(menu)
    db.commit()
    db.refresh(menu)
    return menu
#funcion para crear o actualizar el menú del día para un restaurante, recibe el ID del restaurante, los detalles del menú (descripción, precio, opciones, disponibilidad, si son los últimos platos y la foto), el usuario actual y una sesión de base de datos. Si ya existe un menú para el día actual, lo reemplaza; de lo contrario, crea uno nuevo. Devuelve un objeto MenuOut o lanza una excepción si el restaurante no existe o si el usuario no es el dueño del restaurante.

@router.put("/menus/{menu_id}", response_model=MenuOut)
async def update_menu(
    menu_id: str,
    description: str | None = Form(None),
    price: int | None = Form(None),
    options: str | None = Form(None),  # coma-separado: "Pollo,Pescado,Vegano"
    is_available: bool | None = Form(None),
    is_last_plates: bool | None = Form(None),
    photo: UploadFile | None = File(None),
    current_user: User = Depends(require_owner),
    db: Session = Depends(get_db),
):
    menu = db.query(MenuHistory).filter(MenuHistory.id == menu_id).first()
    if not menu:
        raise HTTPException(status_code=404, detail="Menú no encontrado")
    _get_owned_restaurant(menu.restaurant_id, current_user, db)

    if description is not None:
        menu.description = description
    if price is not None:
        menu.price = price
    if options is not None:
        menu.options = [o.strip() for o in options.split(",") if o.strip()]
    if is_available is not None:
        menu.is_available = is_available
    if is_last_plates is not None:
        menu.is_last_plates = is_last_plates

    # Solo si mandan una foto nueva: subimos la nueva y borramos la vieja.
    # Si no mandan foto, se queda la actual tal cual (no es obligatorio
    # cambiar la imagen cada vez que se edita precio o descripción).
    if photo is not None:
        old_photo = menu.photo_url
        menu.photo_url = await upload_menu_photo(photo, menu.restaurant_id)
        delete_menu_photo(old_photo)

    db.commit()
    db.refresh(menu)
    return menu
#funcion para actualizar un menú existente, recibe el ID del menú, los detalles del menú (descripción, precio, opciones, disponibilidad, si son los últimos platos y la foto), el usuario actual y una sesión de base de datos. Solo actualiza los campos que se proporcionan; si no se proporciona un campo, se mantiene su valor actual. Devuelve un objeto MenuOut o lanza una excepción si no se encuentra el menú o si el usuario no es el dueño del restaurante asociado al menú.


@router.delete("/menus/{menu_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_menu(
    menu_id: str,
    current_user: User = Depends(require_owner),
    db: Session = Depends(get_db),
):
    menu = db.query(MenuHistory).filter(MenuHistory.id == menu_id).first()
    if not menu:
        raise HTTPException(status_code=404, detail="Menú no encontrado")
    _get_owned_restaurant(menu.restaurant_id, current_user, db)

    delete_menu_photo(menu.photo_url)
    db.delete(menu)
    db.commit()
#funcion para eliminar un menú existente, recibe el ID del menú, el usuario actual y una sesión de base de datos, lanza una excepción si no se encuentra el menú o si el usuario no es el dueño del restaurante asociado al menú, y elimina la foto del menú antes de eliminar el registro del menú mismo