"""Loyalty program model — tracks user points and tier status."""
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class LoyaltyAccount(Base):
    __tablename__ = "loyalty_accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    points = Column(Float, default=0.0, nullable=False)
    tier = Column(String(20), default="None", nullable=False)  # None / Silver / Gold / Platinum
    total_flights = Column(Integer, default=0, nullable=False)
    total_spent = Column(Float, default=0.0, nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="loyalty")


TIER_THRESHOLDS = {
    "Platinum": 5000,
    "Gold": 2000,
    "Silver": 500,
}


def calculate_tier(points: float) -> str:
    for tier, threshold in TIER_THRESHOLDS.items():
        if points >= threshold:
            return tier
    return "None"


def points_for_amount(amount: float) -> float:
    """Award 1 point per ₹10 spent."""
    return round(amount / 10, 1)
