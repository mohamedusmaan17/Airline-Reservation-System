import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

# Ensure project root is in sys.path when script is executed directly
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


def generate_pnr():
    """Generate a collision-safe PNR like 'AI-7X3K9M'."""
    return "AI-" + uuid.uuid4().hex[:6].upper()


class Booking(Base):
    __tablename__ = "bookings"

    booking_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    passenger_id = Column(Integer, ForeignKey("passengers.passenger_id"), nullable=False)
    flight_id = Column(Integer, ForeignKey("flights.flight_id"), nullable=False)
    seat_id = Column(Integer, ForeignKey("seats.seat_id"), nullable=True)
    booking_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    seat_number = Column(String(10), nullable=True)
    booking_status = Column(String(20), nullable=False, default="Confirmed")
    pnr = Column(String(20), unique=True, nullable=False, default=generate_pnr, index=True)
    total_amount = Column(Float, default=0.0)
    baggage_allowance = Column(String(50), nullable=True, default="7kg Cabin + 15kg Check-in")
    trip_type = Column(String(20), nullable=True, default="One-Way")


    # Cancellation
    cancelled_at = Column(DateTime, nullable=True)
    refund_status = Column(String(20), nullable=True)  # pending / processed / denied

    # Relationships
    user = relationship("User", back_populates="bookings")
    passenger = relationship("Passenger", back_populates="bookings")
    flight = relationship("Flight", back_populates="bookings")
    seat = relationship("Seat")
    payment = relationship("Payment", back_populates="booking", uselist=False)
    boarding_pass = relationship("BoardingPass", back_populates="booking", uselist=False)
    ticket = relationship("Ticket", back_populates="booking", uselist=False)
