from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.models.vote import VoteHistory
from app.models.menu import MenuHistory
from app.schemas.vote import VoteCreate, VoteOut
from app.core.utils import generate_id, current_timestamp_ms, current_date_str
from app.dependencies import get_current_user

router = APIRouter(tags=["votes"])


@router.post("/votes", response_model=VoteOut, status_code=status.HTTP_201_CREATED)
def submit_vote(
    payload: VoteCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    today = current_date_str()

    already_voted = (
        db.query(VoteHistory)
        .filter(
            VoteHistory.user_id == current_user.uid,
            VoteHistory.restaurant_id == payload.restaurant_id,
            VoteHistory.date == today,
        )
        .first()
    )
    if already_voted:
        raise HTTPException(status_code=400, detail="Ya votaste hoy por este restaurante")

    menu = db.query(MenuHistory).filter(MenuHistory.id == payload.menu_id).first()
    if not menu:
        raise HTTPException(status_code=404, detail="Menú no encontrado")

    vote = VoteHistory(
        id=generate_id("vote_"),
        user_id=current_user.uid,
        restaurant_id=payload.restaurant_id,
        date=today,
        vote_type=payload.vote_type,
        comment=payload.comment,
        timestamp=current_timestamp_ms(),
    )
    db.add(vote)

    if payload.vote_type == "BUENAZO":
        menu.buenazos += 1
    else:
        menu.fatals += 1

    db.commit()
    db.refresh(vote)
    return vote
#funcion para enviar un voto, recibe un payload de tipo VoteCreate, el usuario actual y una sesión de base de datos, verifica si el usuario ya votó hoy por el restaurante y si el menú existe, luego crea un nuevo registro de voto y actualiza los contadores de votos del menú correspondiente, finalmente devuelve un objeto VoteOut

@router.get("/restaurants/{restaurant_id}/votes", response_model=list[VoteOut])
def get_restaurant_votes(restaurant_id: str, db: Session = Depends(get_db)):
    return db.query(VoteHistory).filter(VoteHistory.restaurant_id == restaurant_id).all()#funcion para obtener todos los votos de un restaurante, recibe el ID del restaurante y una sesión de base de datos, devuelve una lista de objetos VoteOut