from sqlalchemy import Column, String, BigInteger
from app.db.database import Base

#modelo de la tabla vote_history, que representa los votos de los usuarios sobre los restaurantes
class VoteHistory(Base):
    __tablename__ = "vote_history"#nombre de la tabla en la base de datos

    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False, index=True)
    restaurant_id = Column(String, nullable=False, index=True)
    date = Column(String, nullable=False)
    vote_type = Column(String, nullable=False)  # "BUENAZO" | "FATAL"
    comment = Column(String, nullable=True)
    timestamp = Column(BigInteger, nullable=False)