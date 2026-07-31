from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Seat(Base):
    """
    Dedicated seat table — Phase 3 foundation.

    Each flight has rows of seats auto-generated when the flight is created.
    Supports seat class, type, pricing addon, and temporary holds for
    preventing double-booking during checkout (Phase 4).
    """
    __tablename__ = "seats"

    seat_id = Column(Integer, primary_key=True, index=True)
    flight_id = Column(Integer, ForeignKey("flights.flight_id", ondelete="CASCADE"), nullable=False, index=True)
    seat_number = Column(String(5), nullable=False)           # e.g. "1A", "12F"
    seat_class = Column(String(20), nullable=False, default="economy")  # economy / business / first
    seat_type = Column(String(10), nullable=False, default="middle")    # window / aisle / middle
    is_booked = Column(Boolean, default=False)
    price_addon = Column(Float, default=0.0)                  # Extra charge for premium seats

    # Seat hold for Phase 4 (prevents double-booking during checkout)
    held_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    held_until = Column(DateTime, nullable=True)

    # Relationships
    flight = relationship("Flight", back_populates="seats")
