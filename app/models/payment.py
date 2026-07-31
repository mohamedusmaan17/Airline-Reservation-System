from datetime import datetime, timezone

# pyrefly: ignore [missing-import]
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Payment(Base):
    __tablename__ = "payments"

    payment_id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.booking_id"), nullable=False)
    amount = Column(Float, nullable=False)
    payment_method = Column(String(30), nullable=True)   # UPI / CREDIT_CARD / DEBIT_CARD / CASH / NETBANKING
    payment_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    payment_status = Column(String(20), nullable=False, default="Pending")  # Success / Failed / Pending
    transaction_id = Column(String(50), nullable=True)

    # Relationships
    booking = relationship("Booking", back_populates="payment")
