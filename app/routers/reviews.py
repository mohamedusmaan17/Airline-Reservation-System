from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.review import Review
from app.models.user import User
from app.routers.ai import SentimentRequest, analyze_sentiment
from app.utils.deps import optional_user

router = APIRouter(prefix="/api/reviews", tags=["Reviews"])


class ReviewCreate(BaseModel):
    flight_id: int | None = None
    rating: int = 5
    review_text: str


@router.post("/")
def create_review(
    data: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(optional_user),
):
    """Submit a customer review with automatic AI sentiment analysis."""
    if not data.review_text.strip():
        raise HTTPException(status_code=400, detail="Review text cannot be empty")

    # Run AI sentiment analysis
    sent_res = analyze_sentiment(SentimentRequest(text=data.review_text))

    review = Review(
        user_id=current_user.id if current_user else None,
        flight_id=data.flight_id,
        rating=max(1, min(5, data.rating)),
        review_text=data.review_text.strip(),
        sentiment=sent_res["sentiment"],
        sentiment_score=sent_res["confidence"],
    )
    db.add(review)
    db.commit()
    db.refresh(review)

    return {
        "message": "Review submitted successfully",
        "review_id": review.review_id,
        "sentiment": sent_res["sentiment"],
        "sentiment_label": sent_res["label"],
        "emoji": sent_res["emoji"],
    }


@router.get("/")
def get_reviews(
    flight_id: int | None = None,
    limit: int = 20,
    db: Session = Depends(get_db),
):
    """Get customer reviews (optionally filtered by flight)."""
    query = db.query(Review)
    if flight_id:
        query = query.filter(Review.flight_id == flight_id)

    reviews = query.order_by(Review.created_at.desc()).limit(limit).all()

    result = []
    for r in reviews:
        user_name = "Anonymous Traveler"
        if r.user:
            user_name = r.user.username

        flight_info = None
        if r.flight:
            flight_info = r.flight.flight_number

        result.append({
            "review_id": r.review_id,
            "user_name": user_name,
            "flight_number": flight_info,
            "rating": r.rating,
            "review_text": r.review_text,
            "sentiment": r.sentiment,
            "sentiment_score": r.sentiment_score,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        })

    return result


@router.get("/summary")
def get_sentiment_summary(db: Session = Depends(get_db)):
    """Get aggregated sentiment breakdown for Admin Dashboard."""
    total = db.query(func.count(Review.review_id)).scalar() or 0
    pos = db.query(func.count(Review.review_id)).filter(Review.sentiment == "positive").scalar() or 0
    neu = db.query(func.count(Review.review_id)).filter(Review.sentiment == "neutral").scalar() or 0
    neg = db.query(func.count(Review.review_id)).filter(Review.sentiment == "negative").scalar() or 0
    avg_rating = db.query(func.avg(Review.rating)).scalar() or 5.0

    return {
        "total_reviews": total,
        "average_rating": round(float(avg_rating), 1),
        "sentiment_counts": {
            "positive": pos,
            "neutral": neu,
            "negative": neg,
        },
        "positive_percentage": round((pos / max(total, 1)) * 100, 1),
    }
