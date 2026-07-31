from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Review(Base):
    __tablename__ = "reviews"

    review_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    flight_id = Column(Integer, ForeignKey("flights.flight_id"), nullable=True)
    rating = Column(Integer, nullable=False, default=5)
    review_text = Column(Text, nullable=False)
    sentiment = Column(String(20), default="positive")  # positive, neutral, negative
    sentiment_score = Column(Float, default=0.8)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user = relationship("User")
    flight = relationship("Flight")
