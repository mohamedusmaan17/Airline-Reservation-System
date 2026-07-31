from sqlalchemy import Column, Integer, String

from app.database import Base


class Airport(Base):
    __tablename__ = "airports"

    airport_id = Column(Integer, primary_key=True, index=True)
    airport_name = Column(String(150), nullable=False)
    airport_code = Column(String(10), unique=True, nullable=False)
    city = Column(String(80), nullable=True)
    country = Column(String(80), nullable=True)
