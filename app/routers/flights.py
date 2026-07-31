from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.airline import Airline
from app.models.airport import Airport
from app.models.flight import Flight
from app.models.seat import Seat
from app.schemas.flight import FlightCreate, FlightResponse, FlightUpdate, SeatResponse
from app.utils.deps import require_admin

router = APIRouter(prefix="/api/flights", tags=["Flights"])


def _build_flight_response(flight: Flight, db: Session) -> dict:
    """Build a FlightResponse dict with resolved names."""
    airline = db.query(Airline).filter(Airline.airline_id == flight.airline_id).first()
    source = db.query(Airport).filter(Airport.airport_id == flight.source_airport).first()
    dest = db.query(Airport).filter(Airport.airport_id == flight.destination_airport).first()
    return {
        "flight_id": flight.flight_id,
        "airline_name": airline.airline_name if airline else None,
        "source_name": source.airport_name if source else None,
        "destination_name": dest.airport_name if dest else None,
        "flight_number": flight.flight_number,
        "departure_time": flight.departure_time,
        "arrival_time": flight.arrival_time,
        "boarding_time": flight.boarding_time,
        "flight_date": flight.flight_date,
        "total_seats": flight.total_seats,
        "available_seats": flight.available_seats,
        "ticket_price": flight.ticket_price,
        "flight_status": flight.flight_status,
        "gate_no": flight.gate_no,
        "terminal_no": flight.terminal_no,
    }


@router.get("/search", response_model=list[FlightResponse])
def search_flights(
    source: str | None = Query(None),
    destination: str | None = Query(None),
    flight_date: date | None = Query(None),
    db: Session = Depends(get_db),
):
    """Search flights with optional filters (public endpoint)."""
    query = db.query(Flight).filter(Flight.flight_status != "Cancelled")

    if source:
        airport = db.query(Airport).filter(Airport.airport_name.ilike(f"%{source}%")).first()
        if airport:
            query = query.filter(Flight.source_airport == airport.airport_id)

    if destination:
        airport = db.query(Airport).filter(Airport.airport_name.ilike(f"%{destination}%")).first()
        if airport:
            query = query.filter(Flight.destination_airport == airport.airport_id)

    if flight_date:
        query = query.filter(Flight.flight_date == flight_date)

    flights = query.order_by(Flight.departure_time).all()
    return [_build_flight_response(f, db) for f in flights]


@router.get("/all", response_model=list[FlightResponse])
def get_all_flights(db: Session = Depends(get_db)):
    """Get all flights (for admin)."""
    flights = db.query(Flight).order_by(Flight.flight_id).all()
    return [_build_flight_response(f, db) for f in flights]


@router.get("/{flight_id}", response_model=FlightResponse)
def get_flight(flight_id: int, db: Session = Depends(get_db)):
    """Get a single flight by ID."""
    flight = db.query(Flight).filter(Flight.flight_id == flight_id).first()
    if not flight:
        raise HTTPException(status_code=404, detail="Flight not found")
    return _build_flight_response(flight, db)


@router.get("/{flight_id}/seats", response_model=list[SeatResponse])
def get_flight_seats(flight_id: int, db: Session = Depends(get_db)):
    """Get the seat map for a flight."""
    flight = db.query(Flight).filter(Flight.flight_id == flight_id).first()
    if not flight:
        raise HTTPException(status_code=404, detail="Flight not found")

    seats = (
        db.query(Seat)
        .filter(Seat.flight_id == flight_id)
        .order_by(Seat.seat_number)
        .all()
    )
    return [SeatResponse.model_validate(s) for s in seats]


def _generate_seats_for_flight(db: Session, flight: Flight):
    """Auto-generate seat rows for a new flight."""
    total = flight.total_seats
    letters = ["A", "B", "C", "D", "E", "F"]
    seat_types = ["window", "middle", "aisle", "aisle", "middle", "window"]
    rows_needed = (total + 5) // 6

    # First 3 rows are business class
    business_rows = min(3, rows_needed)

    for r in range(1, rows_needed + 1):
        for c_idx, letter in enumerate(letters):
            seat_class = "business" if r <= business_rows else "economy"
            price_addon = 1500.0 if seat_class == "business" else (
                300.0 if seat_types[c_idx] == "window" else 0.0
            )
            seat = Seat(
                flight_id=flight.flight_id,
                seat_number=f"{r}{letter}",
                seat_class=seat_class,
                seat_type=seat_types[c_idx],
                price_addon=price_addon,
            )
            db.add(seat)

    db.commit()


@router.post("/", response_model=FlightResponse)
def create_flight(
    data: FlightCreate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    """Create a new flight (admin only)."""
    existing = db.query(Flight).filter(Flight.flight_number == data.flight_number).first()
    if existing:
        raise HTTPException(status_code=400, detail="Flight number already exists")

    flight = Flight(
        airline_id=data.airline_id,
        source_airport=data.source_airport,
        destination_airport=data.destination_airport,
        flight_number=data.flight_number,
        departure_time=data.departure_time,
        arrival_time=data.arrival_time,
        boarding_time=data.boarding_time,
        flight_date=data.flight_date,
        total_seats=data.total_seats,
        available_seats=data.total_seats,
        ticket_price=data.ticket_price,
        flight_status=data.flight_status,
        gate_no=data.gate_no,
        terminal_no=data.terminal_no,
    )
    db.add(flight)
    db.commit()
    db.refresh(flight)

    _generate_seats_for_flight(db, flight)

    return _build_flight_response(flight, db)


@router.put("/{flight_id}", response_model=FlightResponse)
def update_flight(
    flight_id: int,
    data: FlightUpdate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    """Update a flight (admin only)."""
    flight = db.query(Flight).filter(Flight.flight_id == flight_id).first()
    if not flight:
        raise HTTPException(status_code=404, detail="Flight not found")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(flight, key, value)

    db.commit()
    db.refresh(flight)
    return _build_flight_response(flight, db)


@router.delete("/{flight_id}")
def delete_flight(
    flight_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    """Delete a flight (admin only)."""
    flight = db.query(Flight).filter(Flight.flight_id == flight_id).first()
    if not flight:
        raise HTTPException(status_code=404, detail="Flight not found")

    db.delete(flight)
    db.commit()
    return {"message": "Flight deleted successfully"}
