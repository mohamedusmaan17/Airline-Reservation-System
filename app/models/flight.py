import sys
from pathlib import Path

# Ensure project root is in sys.path when script is executed directly
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from sqlalchemy import Column, Date, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Flight(Base):
    __tablename__ = "flights"

    flight_id = Column(Integer, primary_key=True, index=True)
    airline_id = Column(Integer, ForeignKey("airlines.airline_id"), nullable=False)
    source_airport = Column(Integer, ForeignKey("airports.airport_id"), nullable=False)
    destination_airport = Column(Integer, ForeignKey("airports.airport_id"), nullable=False)
    flight_number = Column(String(20), unique=True, nullable=False, index=True)
    departure_time = Column(String(10), nullable=False)   # HH:MM format
    arrival_time = Column(String(10), nullable=False)
    boarding_time = Column(String(10), nullable=True)
    flight_date = Column(Date, nullable=True)
    total_seats = Column(Integer, nullable=False, default=180)
    available_seats = Column(Integer, nullable=False, default=180)
    ticket_price = Column(Float, nullable=False, default=0.0)
    flight_status = Column(String(20), nullable=False, default="Scheduled")
    gate_no = Column(String(10), nullable=True)
    terminal_no = Column(String(10), nullable=True)

    # Relationships
    airline = relationship("Airline", back_populates="flights")
    source = relationship("Airport", foreign_keys="Flight.source_airport")
    destination = relationship("Airport", foreign_keys="Flight.destination_airport")
    seats = relationship("Seat", back_populates="flight", cascade="all, delete-orphan")
    bookings = relationship("Booking", back_populates="flight")
