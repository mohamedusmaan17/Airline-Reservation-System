
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.airline import Airline
from app.models.airport import Airport
from app.models.booking import Booking
from app.models.flight import Flight
from app.models.passenger import Passenger
from app.models.payment import Payment
from app.models.review import Review
from app.schemas.booking import PassengerCreate, PassengerResponse
from app.utils.deps import require_admin

router = APIRouter(prefix="/api/admin", tags=["Admin"])


# ── Dashboard Stats ────────────────────────────────────
@router.get("/dashboard")
def dashboard_stats(db: Session = Depends(get_db)):


    """Get rich dashboard statistics & SQL analytics for the admin panel."""
    total_airlines = db.query(func.count(Airline.airline_id)).scalar() or 0
    total_airports = db.query(func.count(Airport.airport_id)).scalar() or 0
    total_flights = db.query(func.count(Flight.flight_id)).scalar() or 0
    total_passengers = db.query(func.count(Passenger.passenger_id)).scalar() or 0
    total_bookings = db.query(func.count(Booking.booking_id)).scalar() or 0
    total_revenue = db.query(func.coalesce(func.sum(Payment.amount), 0)).filter(
        Payment.payment_status == "Success"
    ).scalar() or 0

    # Bookings by status
    status_counts = (
        db.query(Booking.booking_status, func.count(Booking.booking_id))
        .group_by(Booking.booking_status)
        .all()
    )

    # Payment method breakdown
    payment_methods = (
        db.query(Payment.payment_method, func.count(Payment.payment_id))
        .filter(Payment.payment_status == "Success")
        .group_by(Payment.payment_method)
        .all()
    )

    # Route Popularity & Revenue SQL aggregation
    flights = db.query(Flight).all()
    route_revenue = {}
    occupancy_data = []

    for f in flights:
        src = db.query(Airport).filter(Airport.airport_id == f.source_airport).first()
        dst = db.query(Airport).filter(Airport.airport_id == f.destination_airport).first()
        route_name = f"{src.airport_code if src else 'SRC'} → {dst.airport_code if dst else 'DST'}"

        rev = db.query(func.coalesce(func.sum(Booking.total_amount), 0)).filter(
            Booking.flight_id == f.flight_id,
            Booking.booking_status == "Confirmed"
        ).scalar() or 0

        route_revenue[route_name] = route_revenue.get(route_name, 0) + float(rev)

        occ_pct = round(((f.total_seats - f.available_seats) / max(f.total_seats, 1)) * 100, 1)
        occupancy_data.append({
            "flight_number": f.flight_number,
            "route": route_name,
            "occupancy_pct": occ_pct,
            "available_seats": f.available_seats,
            "total_seats": f.total_seats,
        })

    # Review Sentiment Distribution
    sentiments = (
        db.query(Review.sentiment, func.count(Review.review_id))
        .group_by(Review.sentiment)
        .all()
    )
    sentiment_counts = {"positive": 0, "neutral": 0, "negative": 0}
    for s, c in sentiments:
        if s in sentiment_counts:
            sentiment_counts[s] = c

    # Recent bookings
    recent = (
        db.query(Booking)
        .order_by(Booking.booking_date.desc())
        .limit(6)
        .all()
    )
    recent_data = []
    for b in recent:
        p = db.query(Passenger).filter(Passenger.passenger_id == b.passenger_id).first()
        f = db.query(Flight).filter(Flight.flight_id == b.flight_id).first()
        recent_data.append({
            "booking_id": b.booking_id,
            "pnr": b.pnr,
            "passenger": f"{p.first_name} {p.last_name}" if p else "N/A",
            "flight": f.flight_number if f else "N/A",
            "status": b.booking_status,
            "amount": b.total_amount,
        })

    return {
        "total_airlines": total_airlines,
        "total_airports": total_airports,
        "total_flights": total_flights,
        "total_passengers": total_passengers,
        "total_bookings": total_bookings,
        "total_revenue": total_revenue,
        "booking_status_chart": {s: c for s, c in status_counts},
        "payment_methods_chart": {m: c for m, c in payment_methods},
        "route_revenue": route_revenue,
        "occupancy_rates": occupancy_data,
        "sentiment_chart": sentiment_counts,
        "recent_bookings": recent_data,
    }



# ── Airlines CRUD ──────────────────────────────────────
class AirlineBody(BaseModel):
    airline_name: str
    airline_code: str
    headquarters: str | None = None
    contact_number: str | None = None


@router.get("/airlines")
def list_airlines(db: Session = Depends(get_db)):
    return [
        {"airline_id": a.airline_id, "airline_name": a.airline_name, "airline_code": a.airline_code,
         "headquarters": a.headquarters, "contact_number": a.contact_number}
        for a in db.query(Airline).order_by(Airline.airline_id).all()
    ]


@router.post("/airlines")
def create_airline(data: AirlineBody, db: Session = Depends(get_db), admin=Depends(require_admin)):
    airline = Airline(**data.model_dump())
    db.add(airline)
    db.commit()
    db.refresh(airline)
    return {"message": "Airline created", "airline_id": airline.airline_id}


@router.put("/airlines/{airline_id}")
def update_airline(airline_id: int, data: AirlineBody, db: Session = Depends(get_db), admin=Depends(require_admin)):
    airline = db.query(Airline).filter(Airline.airline_id == airline_id).first()
    if not airline:
        raise HTTPException(status_code=404, detail="Airline not found")
    for k, v in data.model_dump().items():
        setattr(airline, k, v)
    db.commit()
    return {"message": "Airline updated"}


@router.delete("/airlines/{airline_id}")
def delete_airline(airline_id: int, db: Session = Depends(get_db), admin=Depends(require_admin)):
    airline = db.query(Airline).filter(Airline.airline_id == airline_id).first()
    if not airline:
        raise HTTPException(status_code=404, detail="Airline not found")
    db.delete(airline)
    db.commit()
    return {"message": "Airline deleted"}


# ── Airports CRUD ──────────────────────────────────────
class AirportBody(BaseModel):
    airport_name: str
    airport_code: str
    city: str | None = None
    country: str | None = None


@router.get("/airports")
def list_airports(db: Session = Depends(get_db)):
    return [
        {"airport_id": a.airport_id, "airport_name": a.airport_name, "airport_code": a.airport_code,
         "city": a.city, "country": a.country}
        for a in db.query(Airport).order_by(Airport.airport_id).all()
    ]


@router.post("/airports")
def create_airport(data: AirportBody, db: Session = Depends(get_db), admin=Depends(require_admin)):
    airport = Airport(**data.model_dump())
    db.add(airport)
    db.commit()
    db.refresh(airport)
    return {"message": "Airport created", "airport_id": airport.airport_id}


@router.put("/airports/{airport_id}")
def update_airport(airport_id: int, data: AirportBody, db: Session = Depends(get_db), admin=Depends(require_admin)):
    airport = db.query(Airport).filter(Airport.airport_id == airport_id).first()
    if not airport:
        raise HTTPException(status_code=404, detail="Airport not found")
    for k, v in data.model_dump().items():
        setattr(airport, k, v)
    db.commit()
    return {"message": "Airport updated"}


@router.delete("/airports/{airport_id}")
def delete_airport(airport_id: int, db: Session = Depends(get_db), admin=Depends(require_admin)):
    airport = db.query(Airport).filter(Airport.airport_id == airport_id).first()
    if not airport:
        raise HTTPException(status_code=404, detail="Airport not found")
    db.delete(airport)
    db.commit()
    return {"message": "Airport deleted"}


# ── Passengers CRUD ────────────────────────────────────
@router.get("/passengers")
def list_passengers(db: Session = Depends(get_db)):
    return [
        PassengerResponse.model_validate(p)
        for p in db.query(Passenger).order_by(Passenger.passenger_id).all()
    ]


@router.post("/passengers")
def create_passenger(data: PassengerCreate, db: Session = Depends(get_db)):
    from datetime import date as date_type
    passenger_data = data.model_dump()
    if passenger_data.get("date_of_birth") and isinstance(passenger_data["date_of_birth"], str):
        try:
            passenger_data["date_of_birth"] = date_type.fromisoformat(passenger_data["date_of_birth"])
        except ValueError:
            passenger_data["date_of_birth"] = None

    existing_passenger = None
    passport = passenger_data.get("passport_number")
    email = passenger_data.get("email")

    if passport:
        existing_passenger = db.query(Passenger).filter(Passenger.passport_number == passport).first()
    if not existing_passenger and email:
        existing_passenger = db.query(Passenger).filter(Passenger.email == email).first()

    if existing_passenger:
        for k, v in passenger_data.items():
            if v is not None:
                setattr(existing_passenger, k, v)
        db.commit()
        db.refresh(existing_passenger)
        return {"message": "Passenger updated", "passenger_id": existing_passenger.passenger_id}

    passenger = Passenger(**passenger_data)
    db.add(passenger)
    db.commit()
    db.refresh(passenger)
    return {"message": "Passenger created", "passenger_id": passenger.passenger_id}



@router.put("/passengers/{passenger_id}")
def update_passenger(passenger_id: int, data: PassengerCreate, db: Session = Depends(get_db)):
    passenger = db.query(Passenger).filter(Passenger.passenger_id == passenger_id).first()
    if not passenger:
        raise HTTPException(status_code=404, detail="Passenger not found")
    from datetime import date as date_type
    update_data = data.model_dump()
    if update_data.get("date_of_birth") and isinstance(update_data["date_of_birth"], str):
        try:
            update_data["date_of_birth"] = date_type.fromisoformat(update_data["date_of_birth"])
        except ValueError:
            update_data["date_of_birth"] = None
    for k, v in update_data.items():
        setattr(passenger, k, v)
    db.commit()
    return {"message": "Passenger updated"}


@router.delete("/passengers/{passenger_id}")
def delete_passenger(passenger_id: int, db: Session = Depends(get_db), admin=Depends(require_admin)):
    passenger = db.query(Passenger).filter(Passenger.passenger_id == passenger_id).first()
    if not passenger:
        raise HTTPException(status_code=404, detail="Passenger not found")
    db.delete(passenger)
    db.commit()
    return {"message": "Passenger deleted"}


# ── Payments ───────────────────────────────────────────
@router.get("/payments")
def list_payments(db: Session = Depends(get_db), admin=Depends(require_admin)):
    payments = db.query(Payment).order_by(Payment.payment_id.desc()).all()
    result = []
    for pay in payments:
        booking = db.query(Booking).filter(Booking.booking_id == pay.booking_id).first()
        p_name = "N/A"
        f_num = "N/A"
        if booking:
            passenger = db.query(Passenger).filter(Passenger.passenger_id == booking.passenger_id).first()
            flight = db.query(Flight).filter(Flight.flight_id == booking.flight_id).first()
            p_name = f"{passenger.first_name} {passenger.last_name}" if passenger else "N/A"
            f_num = flight.flight_number if flight else "N/A"

        result.append({
            "payment_id": pay.payment_id,
            "booking_id": pay.booking_id,
            "passenger": p_name,
            "flight": f_num,
            "amount": pay.amount,
            "payment_method": pay.payment_method,
            "payment_date": pay.payment_date.isoformat() if pay.payment_date else None,
            "payment_status": pay.payment_status,
            "transaction_id": pay.transaction_id,
        })
    return result
