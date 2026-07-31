from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class BoardingPass(Base):
    __tablename__ = "boarding_passes"

    boarding_id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.booking_id"), nullable=False, unique=True)
    boarding_number = Column(String(20), unique=True, nullable=False)
    gate_no = Column(String(10), nullable=True)
    boarding_time = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    checkin_status = Column(String(20), default="Checked In")

    # Relationships
    booking = relationship("Booking", back_populates="boarding_pass")
