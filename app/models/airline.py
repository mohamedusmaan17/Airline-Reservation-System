from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Airline(Base):
    __tablename__ = "airlines"

    airline_id = Column(Integer, primary_key=True, index=True)
    airline_name = Column(String(100), nullable=False)
    airline_code = Column(String(10), unique=True, nullable=False)
    headquarters = Column(String(100), nullable=True)
    contact_number = Column(String(30), nullable=True)

    # Relationships
    flights = relationship("Flight", back_populates="airline")
