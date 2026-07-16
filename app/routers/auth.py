from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from app.schemas.user import UserOut
from app.core.security import hash_password, verify_password, create_access_token
from app.core.utils import generate_id, current_timestamp_ms
from app.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])

# Rutas de autenticación
@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Ese correo ya está registrado")
    # Crear un nuevo usuario y guardarlo en la base de datos
    user = User(#llamada de clase user
        uid=generate_id("user_"),
        email=payload.email,
        display_name=payload.display_name,
        password=hash_password(payload.password),
        role=payload.role,
        photo_url=None,
        created_at=current_timestamp_ms(),
    )
    db.add(user)
    db.commit()

    token = create_access_token({"sub": user.uid})
    return TokenResponse(access_token=token)

# Rutas de inicio de sesión y obtención del usuario actual
@router.post("/login", response_model=TokenResponse)
# Funcion login  
def login(payload: LoginRequest, db: Session = Depends(get_db)):# funcion para iniciar sesión, recibe un payload de tipo LoginRequest y una sesión de base de datos
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password):
        raise HTTPException(status_code=401, detail="Correo o contraseña incorrectos")

    token = create_access_token({"sub": user.uid})
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(current_user: User = Depends(get_current_user)):
    # Con JWT no hay sesión que destruir en el servidor: el token sigue
    # siendo válido hasta que expira. El cierre de sesión real ocurre
    # en el cliente, borrando el token guardado en DataStore.
    # Este endpoint existe para mantener el mismo contrato que
    # FirebaseDataSource.logout() y darle un punto de entrada a la API.
    return