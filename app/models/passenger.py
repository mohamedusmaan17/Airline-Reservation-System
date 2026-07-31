from sqlalchemy import Column, Date, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Passenger(Base):
    __tablename__ = "passengers"

    passenger_id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    gender = Column(String(10), nullable=True)
    date_of_birth = Column(Date, nullable=True)
    phone = Column(String(30), nullable=True)
    email = Column(String(120), nullable=True, index=True)
    passport_number = Column(String(20), unique=True, nullable=True, index=True)
    nationality = Column(String(50), nullable=True)

    # Relationships
    bookings = relationship("Booking", back_populates="passenger")
