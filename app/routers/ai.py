"""
AI-Powered Features Router
Implements simulated ML features: price prediction, delay estimation,
seat recommendation, carbon footprint, sentiment analysis, and chatbot.
"""
import math
import random
import re
from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.airport import Airport
from app.models.flight import Flight
from app.models.seat import Seat

router = APIRouter(prefix="/api/ai", tags=["AI Features"])


# ── Request / Response Schemas ─────────────────────────────────────────────────

class PricePredictionRequest(BaseModel):
    flight_id: int


class SentimentRequest(BaseModel):
    text: str


class ChatbotRequest(BaseModel):
    message: str
    context: dict | None = None


# ── Utility: Haversine Distance ────────────────────────────────────────────────

def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Compute great-circle distance in km between two lat/lon points."""
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


# Approximate lat/lon for major Indian airports (by airport_code pattern)
AIRPORT_COORDS: dict[str, tuple[float, float]] = {
    "DEL": (28.5562, 77.1000),
    "BOM": (19.0896, 72.8656),
    "BLR": (13.1986, 77.7066),
    "HYD": (17.2403, 78.4294),
    "MAA": (12.9941, 80.1709),
    "CCU": (22.6547, 88.4467),
    "COK": (10.1520, 76.4019),
    "AMD": (23.0726, 72.6347),
    "GOI": (15.3808, 73.8314),
    "PNQ": (18.5822, 73.9197),
    "JAI": (26.8242, 75.8122),
    "LKO": (26.7606, 80.8893),
}


def _get_coords(airport_code: str) -> tuple[float, float]:
    return AIRPORT_COORDS.get(airport_code, (20.5937, 78.9629))  # Default: India center


def _airport_distance_km(db: Session, source_id: int, dest_id: int) -> float:
    """Estimate distance between two airports using their codes."""
    src = db.query(Airport).filter(Airport.airport_id == source_id).first()
    dst = db.query(Airport).filter(Airport.airport_id == dest_id).first()
    if not src or not dst:
        return 1500.0  # Default fallback

    src_coords = _get_coords(src.airport_code or "")
    dst_coords = _get_coords(dst.airport_code or "")
    return _haversine_km(*src_coords, *dst_coords)


# ── Endpoint 1: Price Prediction ───────────────────────────────────────────────

@router.post("/price-prediction")
def predict_price(req: PricePredictionRequest, db: Session = Depends(get_db)):
    """
    Simulates a fare-trend ML model.
    Returns a price forecast and a nudge message.
    """
    flight = db.query(Flight).filter(Flight.flight_id == req.flight_id).first()
    if not flight:
        raise HTTPException(status_code=404, detail="Flight not found")

    # Simulate demand signal: low availability → higher predicted price change
    occupancy = 1 - (flight.available_seats / max(flight.total_seats, 1))
    days_to_flight = 30
    if flight.flight_date:
        delta = (flight.flight_date - date.today()).days
        days_to_flight = max(0, delta)

    # Price pressure score (0–100)
    pressure = (occupancy * 60) + (max(0, 14 - days_to_flight) * 2.5)
    pressure = min(100, pressure)

    if pressure > 70:
        direction = "rising"
        pct = round(random.uniform(12, 25), 1)
        urgency = "high"
        message = f"🔥 Prices are expected to rise by ~{pct}% within 48 hours. Book now to lock in this fare!"
    elif pressure > 40:
        direction = "rising"
        pct = round(random.uniform(5, 12), 1)
        urgency = "medium"
        message = f"📈 Demand is picking up. Price may increase by ~{pct}% soon. Consider booking today."
    else:
        direction = "stable"
        pct = round(random.uniform(1, 5), 1)
        urgency = "low"
        message = "✅ Fare is currently stable. You have a few days to decide, but availability is limited."

    return {
        "flight_id": flight.flight_id,
        "flight_number": flight.flight_number,
        "current_price": flight.ticket_price,
        "price_direction": direction,
        "predicted_change_pct": pct,
        "urgency": urgency,
        "occupancy_pct": round(occupancy * 100, 1),
        "days_to_flight": days_to_flight,
        "message": message,
    }


# ── Endpoint 2: Delay Prediction ──────────────────────────────────────────────

@router.get("/delay-prediction/{flight_id}")
def predict_delay(flight_id: int, db: Session = Depends(get_db)):
    """
    Simulates a delay classification model.
    Delay probability is based on route load, day of week, and departure hour.
    """
    flight = db.query(Flight).filter(Flight.flight_id == flight_id).first()
    if not flight:
        raise HTTPException(status_code=404, detail="Flight not found")

    # Simulate feature engineering
    try:
        dep_hour = int(flight.departure_time.split(":")[0])
    except Exception:
        dep_hour = 12

    day_of_week = 3  # Default Wednesday
    if flight.flight_date:
        day_of_week = flight.flight_date.weekday()

    # Higher delay risk: early morning, Fri/Sun, busy routes
    base_risk = 15
    if dep_hour < 7:
        base_risk += 20  # Early morning delays
    elif dep_hour > 17:
        base_risk += 15  # Evening cascade delays
    if day_of_week in (4, 6):  # Friday, Sunday
        base_risk += 12
    occupancy = 1 - (flight.available_seats / max(flight.total_seats, 1))
    base_risk += occupancy * 10

    delay_prob = min(95, max(5, round(base_risk + random.uniform(-3, 3), 1)))

    if delay_prob < 25:
        level = "low"
        icon = "✅"
        label = "On-Time Likely"
        expected_delay = "< 10 min"
    elif delay_prob < 55:
        level = "medium"
        icon = "⚠️"
        label = "Minor Delay Possible"
        expected_delay = "15–30 min"
    else:
        level = "high"
        icon = "🔴"
        label = "Significant Delay Risk"
        expected_delay = "30–60 min"

    return {
        "flight_id": flight_id,
        "flight_number": flight.flight_number,
        "delay_probability_pct": delay_prob,
        "delay_level": level,
        "label": label,
        "icon": icon,
        "expected_delay": expected_delay,
        "factors": {
            "departure_hour": dep_hour,
            "occupancy_pct": round(occupancy * 100, 1),
            "day_of_week": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][day_of_week],
        },
    }


# ── Endpoint 3: Seat Recommendation ───────────────────────────────────────────

@router.get("/seat-recommendation/{flight_id}")
def recommend_seats(flight_id: int, db: Session = Depends(get_db)):
    """
    Returns top 3 seat recommendations.
    Logic: prioritize window seats in economy, early rows for business.
    """
    seats = (
        db.query(Seat)
        .filter(Seat.flight_id == flight_id, Seat.is_booked == False)  # noqa: E712
        .all()
    )
    if not seats:
        raise HTTPException(status_code=404, detail="No available seats found")

    def score_seat(s: Seat) -> float:
        score = 0.0
        if s.seat_class == "business":
            score += 50
        if s.seat_type == "window":
            score += 30
        if s.seat_type == "aisle":
            score += 15
        # Prefer earlier rows (lower number)
        try:
            row = int(re.sub(r"\D", "", s.seat_number))
            score -= row * 0.5
        except ValueError:
            pass
        return score

    top_seats = sorted(seats, key=score_seat, reverse=True)[:3]

    return {
        "flight_id": flight_id,
        "recommendations": [
            {
                "seat_id": s.seat_id,
                "seat_number": s.seat_number,
                "seat_class": s.seat_class,
                "seat_type": s.seat_type,
                "price_addon": s.price_addon,
                "reason": (
                    "🏆 Premium window in Business Class" if s.seat_class == "business" and s.seat_type == "window"
                    else "⭐ Business Class comfort" if s.seat_class == "business"
                    else "🪟 Window seat with a view" if s.seat_type == "window"
                    else "🚶 Easy aisle access" if s.seat_type == "aisle"
                    else "✅ Great value economy seat"
                ),
            }
            for s in top_seats
        ],
    }


# ── Endpoint 4: Carbon Footprint ──────────────────────────────────────────────

@router.get("/carbon/{flight_id}")
def carbon_footprint(flight_id: int, db: Session = Depends(get_db)):
    """
    Estimates CO₂ emissions for a flight.
    Formula: distance_km × 0.255 kg CO₂/km/passenger (ICAO standard)
    """
    flight = db.query(Flight).filter(Flight.flight_id == flight_id).first()
    if not flight:
        raise HTTPException(status_code=404, detail="Flight not found")

    distance_km = _airport_distance_km(db, flight.source_airport, flight.destination_airport)

    # ICAO emission factor: ~0.255 kg CO₂ per km per passenger (economy)
    co2_kg = round(distance_km * 0.255, 1)
    co2_kg_business = round(co2_kg * 2.0, 1)  # Business class ~2x footprint

    # Equivalents
    car_km_equiv = round(co2_kg / 0.21, 0)    # 0.21 kg CO₂/km average car
    trees_to_offset = round(co2_kg / 21.7, 1)  # A tree absorbs ~21.7 kg CO₂/year

    # Comparison to average
    if co2_kg < 50:
        rating = "A"
        label = "Very Low Emissions"
        color = "#10b981"
    elif co2_kg < 120:
        rating = "B"
        label = "Low Emissions"
        color = "#84cc16"
    elif co2_kg < 200:
        rating = "C"
        label = "Moderate Emissions"
        color = "#f59e0b"
    else:
        rating = "D"
        label = "High Emissions"
        color = "#ef4444"

    return {
        "flight_id": flight_id,
        "flight_number": flight.flight_number,
        "distance_km": round(distance_km, 0),
        "co2_kg_economy": co2_kg,
        "co2_kg_business": co2_kg_business,
        "car_km_equivalent": int(car_km_equiv),
        "trees_to_offset": trees_to_offset,
        "emission_rating": rating,
        "emission_label": label,
        "rating_color": color,
    }


# ── Endpoint 5: Sentiment Analysis ────────────────────────────────────────────

_POSITIVE_WORDS = {
    "excellent", "amazing", "great", "wonderful", "fantastic", "best", "good",
    "love", "loved", "perfect", "smooth", "comfortable", "helpful", "clean",
    "punctual", "on time", "friendly", "courteous", "delicious", "nice", "happy",
    "recommend", "superb", "awesome", "outstanding",
}

_NEGATIVE_WORDS = {
    "terrible", "horrible", "awful", "bad", "worst", "poor", "dirty", "rude",
    "late", "delayed", "cancelled", "uncomfortable", "noisy", "unhelpful",
    "cold", "broken", "disappointed", "never again", "waste", "expensive",
    "crowded", "cramped", "missing", "lost", "disgusting",
}


@router.post("/sentiment")
def analyze_sentiment(req: SentimentRequest):
    """
    Keyword-based sentiment analysis for customer reviews.
    Returns: positive / negative / neutral with a confidence score.
    """
    text_lower = req.text.lower()
    words = re.findall(r"\b\w+\b", text_lower)
    bigrams = [" ".join(words[i:i+2]) for i in range(len(words) - 1)]
    all_tokens = words + bigrams

    pos_hits = sum(1 for t in all_tokens if t in _POSITIVE_WORDS)
    neg_hits = sum(1 for t in all_tokens if t in _NEGATIVE_WORDS)

    total = pos_hits + neg_hits
    if total == 0:
        sentiment = "neutral"
        confidence = 0.55
        emoji = "😐"
        color = "#64748b"
    elif pos_hits > neg_hits:
        sentiment = "positive"
        confidence = round(0.5 + (pos_hits / max(total, 1)) * 0.45, 2)
        emoji = "😊"
        color = "#10b981"
    else:
        sentiment = "negative"
        confidence = round(0.5 + (neg_hits / max(total, 1)) * 0.45, 2)
        emoji = "😞"
        color = "#ef4444"

    return {
        "text": req.text,
        "sentiment": sentiment,
        "confidence": confidence,
        "emoji": emoji,
        "color": color,
        "positive_indicators": pos_hits,
        "negative_indicators": neg_hits,
        "label": f"{emoji} {sentiment.capitalize()} ({round(confidence * 100)}% confidence)",
    }


# ── Endpoint 6: AI Chatbot ────────────────────────────────────────────────────

_INTENTS = [
    {
        "patterns": ["book", "flight to", "book me", "ticket to", "fly to", "reserve"],
        "intent": "book_flight",
        "response": "✈️ I'd love to help you book a flight! Use the **Search Flights** page — just enter your source city, destination, and date. I'll find the best options for you.",
    },
    {
        "patterns": ["cancel", "cancellation", "refund", "money back"],
        "intent": "cancel_booking",
        "response": "🔄 To cancel a booking, go to **My Bookings** and click **Cancel Booking**. Refunds are processed within 5–7 business days. Need help with a specific PNR?",
    },
    {
        "patterns": ["seat", "window", "aisle", "business", "economy", "upgrade"],
        "intent": "seat_query",
        "response": "🪑 After selecting your flight, you'll see an **interactive seat map**. Window seats (A, F) and Business class rows (1–3) are available. Business adds ₹1,500 to your fare.",
    },
    {
        "patterns": ["check in", "checkin", "boarding pass", "gate", "terminal"],
        "intent": "checkin",
        "response": "🎫 Online check-in is available through **My Bookings → Check-In**. Your boarding pass number and gate will be displayed instantly. Remember to arrive 2 hours before departure!",
    },
    {
        "patterns": ["price", "fare", "cost", "cheap", "expensive", "how much"],
        "intent": "price_query",
        "response": "💰 Fares vary by route and date. Economy seats start from ₹3,500 on domestic routes. Check the **Search Flights** page for real-time pricing. Pro tip: prices rise closer to the date!",
    },
    {
        "patterns": ["delay", "late", "on time", "status", "track"],
        "intent": "flight_status",
        "response": "🛫 You can track your flight status in **My Bookings**. Live delay predictions are shown on each flight card. Need to check a specific flight number?",
    },
    {
        "patterns": ["baggage", "luggage", "bag", "carry on", "weight"],
        "intent": "baggage",
        "response": "🧳 Baggage allowance:\n• **Economy**: 15 kg check-in + 7 kg cabin\n• **Business**: 25 kg check-in + 10 kg cabin\nExcess baggage fees apply at the airport.",
    },
    {
        "patterns": ["loyalty", "points", "miles", "rewards", "silver", "gold", "platinum"],
        "intent": "loyalty",
        "response": "⭐ Our SkyBooker Rewards program awards **1 point per ₹10** spent. Check **My Loyalty** in your account for your tier status:\n• 🥈 Silver: 500+ points\n• 🥇 Gold: 2,000+ points\n• 💎 Platinum: 5,000+ points",
    },
    {
        "patterns": ["contact", "support", "help", "customer care", "phone", "email"],
        "intent": "support",
        "response": "📞 Customer Support:\n• **Phone**: 1800-XXX-XXXX (24/7)\n• **Email**: support@skybooker.in\n• **Live chat**: That's me! I'm here to help 😊",
    },
    {
        "patterns": ["hi", "hello", "hey", "good morning", "good evening", "hola"],
        "intent": "greeting",
        "response": "👋 Hello! Welcome to **SkyBooker AI Assistant**. I can help you with:\n• Booking flights\n• Seat selection\n• Cancellations & refunds\n• Check-in & boarding passes\n• Baggage info\n\nWhat can I help you with today?",
    },
    {
        "patterns": ["thank", "thanks", "great thanks", "thank you"],
        "intent": "thanks",
        "response": "😊 You're welcome! Have a wonderful flight. Is there anything else I can help you with?",
    },
    {
        "patterns": ["carbon", "environment", "co2", "emission", "green", "eco"],
        "intent": "carbon",
        "response": "🌿 Great question! We calculate the **carbon footprint** of every flight based on route distance using ICAO emission factors. You can see the CO₂ estimate on each flight card. Consider offsetting your emissions by planting trees!",
    },
]


@router.post("/chatbot")
def chatbot(req: ChatbotRequest):
    """
    Intent-classification chatbot using keyword matching.
    Returns a canned response based on matched intent.
    """
    message_lower = req.message.lower()

    best_intent = None
    best_score = 0

    for intent_def in _INTENTS:
        score = sum(1 for pattern in intent_def["patterns"] if pattern in message_lower)
        if score > best_score:
            best_score = score
            best_intent = intent_def

    if best_intent and best_score > 0:
        return {
            "intent": best_intent["intent"],
            "response": best_intent["response"],
            "confidence": min(0.95, 0.6 + best_score * 0.1),
        }

    # Fallback
    return {
        "intent": "unknown",
        "response": "🤔 I'm not sure I understood that. Could you rephrase? I can help with **bookings, cancellations, seat selection, check-in, baggage, and loyalty rewards**.",
        "confidence": 0.0,
    }


# ── Endpoint 7: OCR ID Extraction ─────────────────────────────────────────────

class OCRRequest(BaseModel):
    image_base64: str | None = None
    document_type: str = "passport"


@router.post("/ocr-extract")
def extract_id_data(req: OCRRequest):
    """
    Simulates OCR ID extraction from uploaded passport/ID photo.
    Returns parsed passenger details.
    """
    sample_first_names = ["Rahul", "Priya", "Mohamed", "Ananya", "Rohan", "Sneha", "Vikram", "Neha"]
    sample_last_names = ["Sharma", "Verma", "Usmaan", "Kapoor", "Patel", "Singh", "Reddy", "Gupta"]

    first_name = random.choice(sample_first_names)
    last_name = random.choice(sample_last_names)
    passport_num = f"{chr(random.randint(65, 90))}{random.randint(1000000, 9999999)}"
    dob_year = random.randint(1985, 2002)
    dob_month = f"{random.randint(1, 12):02d}"
    dob_day = f"{random.randint(1, 28):02d}"

    return {
        "status": "success",
        "confidence": 0.94,
        "extracted_data": {
            "first_name": first_name,
            "last_name": last_name,
            "gender": random.choice(["Male", "Female"]),
            "date_of_birth": f"{dob_year}-{dob_month}-{dob_day}",
            "passport_number": passport_num,
            "nationality": "India",
            "document_type": req.document_type.upper(),
        },
        "message": "⚡ Passport ID details extracted successfully!",
    }


# ── Endpoint 8: Fraud & Anomaly Detection ──────────────────────────────────────

class FraudCheckRequest(BaseModel):
    user_id: int | None = None
    email: str | None = None
    payment_method: str = "UPI"
    amount: float = 5000.0


@router.post("/fraud-check")
def check_fraud_risk(req: FraudCheckRequest, db: Session = Depends(get_db)):
    """
    Simulates SQL + ML anomaly detection for rapid / suspicious booking patterns.
    """
    risk_score = random.randint(5, 30)  # Standard low risk
    flags = []

    if req.amount > 30000:
        risk_score += 25
        flags.append("High transaction value")

    if req.payment_method == "CREDIT_CARD" and random.random() > 0.8:
        risk_score += 20
        flags.append("Card country mismatch")

    is_flagged = risk_score > 50

    return {
        "risk_score": risk_score,
        "risk_level": "High Risk ⚠️" if is_flagged else "Low Risk ✅",
        "is_flagged": is_flagged,
        "anomaly_flags": flags if flags else ["Normal activity pattern"],
        "recommendation": "Manual approval needed" if is_flagged else "Transaction clear",
    }

