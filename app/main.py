from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.database import Base, engine
from app.routers import auth, restaurants, menus, votes, favorites

# Crea las tablas si no existen todavía. Para un proyecto en producción real
# se usaría Alembic (migraciones versionadas), pero para este entregable
# académico esto es suficiente y evita otra capa de complejidad.
Base.metadata.create_all(bind=engine)

app = FastAPI(title="MenuFinderPE API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(restaurants.router)
app.include_router(menus.router)
app.include_router(votes.router)
app.include_router(favorites.router)


@app.get("/")
def health_check():
    return {"status": "ok"}