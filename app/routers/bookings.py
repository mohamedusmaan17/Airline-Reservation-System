import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.boarding_pass import BoardingPass
from app.models.booking import Booking
from app.models.flight import Flight
from app.models.passenger import Passenger
from app.models.payment import Payment
from app.models.seat import Seat
from app.models.user import User
from app.schemas.booking import BookingCreate, BookingResponse
from app.utils.deps import get_current_user

router = APIRouter(prefix="/api/bookings", tags=["Bookings"])


def _build_booking_response(b: Booking, db: Session) -> dict:
    passenger = db.query(Passenger).filter(Passenger.passenger_id == b.passenger_id).first()
    flight = db.query(Flight).filter(Flight.flight_id == b.flight_id).first()
    return {
        "booking_id": b.booking_id,
        "pnr": b.pnr,
        "passenger_name": f"{passenger.first_name} {passenger.last_name}" if passenger else None,
        "flight_number": flight.flight_number if flight else None,
        "seat_number": b.seat_number,
        "booking_date": b.booking_date,
        "booking_status": b.booking_status,
        "total_amount": b.total_amount or 0,
        "refund_status": b.refund_status,
        "baggage_allowance": getattr(b, 'baggage_allowance', '7kg Cabin + 15kg Check-in') or "7kg Cabin + 15kg Check-in",
        "trip_type": getattr(b, 'trip_type', 'One-Way') or "One-Way",
    }


@router.post("/", response_model=BookingResponse)
def create_booking(
    data: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new booking with seat selection.

    This uses a basic check-then-insert approach.
    Phase 4 will upgrade this to use SELECT ... FOR UPDATE
    with proper transaction locking.
    """
    # Validate flight exists
    flight = db.query(Flight).filter(Flight.flight_id == data.flight_id).first()
    if not flight:
        raise HTTPException(status_code=404, detail="Flight not found")

    if flight.available_seats <= 0:
        raise HTTPException(status_code=400, detail="Flight is fully booked")

    # Validate seat exists and is available
    seat = db.query(Seat).filter(Seat.seat_id == data.seat_id).first()
    if not seat:
        raise HTTPException(status_code=404, detail="Seat not found")
    if seat.is_booked:
        raise HTTPException(status_code=400, detail="Seat is already booked")

    # Validate passenger
    passenger = db.query(Passenger).filter(Passenger.passenger_id == data.passenger_id).first()
    if not passenger:
        raise HTTPException(status_code=404, detail="Passenger not found")

    # Calculate total
    total_amount = flight.ticket_price + seat.price_addon

    # Create booking
    booking = Booking(
        user_id=current_user.id,
        passenger_id=data.passenger_id,
        flight_id=data.flight_id,
        seat_id=data.seat_id,
        seat_number=seat.seat_number,
        booking_status="Confirmed",
        total_amount=total_amount,
        baggage_allowance=data.baggage_allowance or "7kg Cabin + 15kg Check-in",
        trip_type=data.trip_type or "One-Way",
    )

    db.add(booking)

    # Mark seat as booked
    seat.is_booked = True

    # Decrement available seats
    flight.available_seats -= 1

    db.commit()
    db.refresh(booking)

    # Auto-create a successful payment record (mock)
    payment = Payment(
        booking_id=booking.booking_id,
        amount=total_amount,
        payment_method=data.payment_method or "UPI",
        payment_status="Success",
        transaction_id=f"TXN-{uuid.uuid4().hex[:8].upper()}",
    )
    db.add(payment)
    db.commit()

    # Automatically generate ticket PDF, store in tickets folder & save to SQL DB
    try:
        generate_and_save_ticket(booking, db)
    except Exception as e:
        print(f"Warning: Failed to pre-generate ticket PDF: {e}")

    return _build_booking_response(booking, db)


@router.get("/my", response_model=list[BookingResponse])
def get_my_bookings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all bookings for the logged-in user."""
    bookings = (
        db.query(Booking)
        .filter(Booking.user_id == current_user.id)
        .order_by(Booking.booking_date.desc())
        .all()
    )
    return [_build_booking_response(b, db) for b in bookings]


@router.get("/all", response_model=list[BookingResponse])
def get_all_bookings(db: Session = Depends(get_db)):
    """Get all bookings (for admin)."""
    bookings = db.query(Booking).order_by(Booking.booking_id.desc()).all()
    return [_build_booking_response(b, db) for b in bookings]


def generate_and_save_ticket(booking: Booking, db: Session) -> bytes:
    """Generate ticket PDF, save to tickets folder, and persist BLOB & path in SQL DB."""
    from pathlib import Path
    from app.models.airline import Airline
    from app.models.airport import Airport
    from app.models.ticket import Ticket
    from app.utils.pdf_generator import generate_ticket_pdf

    passenger = db.query(Passenger).filter(Passenger.passenger_id == booking.passenger_id).first()
    flight = db.query(Flight).filter(Flight.flight_id == booking.flight_id).first()
    seat = db.query(Seat).filter(Seat.seat_id == booking.seat_id).first() if booking.seat_id else None
    payment = db.query(Payment).filter(Payment.booking_id == booking.booking_id).first()

    airline_name = "SkyBooker Express"
    source_name = "Origin"
    destination_name = "Destination"

    if flight:
        airline = db.query(Airline).filter(Airline.airline_id == flight.airline_id).first()
        src = db.query(Airport).filter(Airport.airport_id == flight.source_airport).first()
        dst = db.query(Airport).filter(Airport.airport_id == flight.destination_airport).first()
        if airline:
            airline_name = airline.airline_name
        if src:
            source_name = f"{src.city} ({src.airport_code})"
        if dst:
            destination_name = f"{dst.city} ({dst.airport_code})"

    pnr = booking.pnr or f"SK-{booking.booking_id}"

    pdf_bytes = generate_ticket_pdf(
        pnr=pnr,
        passenger_name=f"{passenger.first_name} {passenger.last_name}" if passenger else "Passenger",
        email=passenger.email if passenger else "n/a",
        phone=passenger.phone if passenger else "n/a",
        flight_number=flight.flight_number if flight else "SK101",
        airline_name=airline_name,
        source_name=source_name,
        destination_name=destination_name,
        departure_time=flight.departure_time if flight else "06:00",
        arrival_time=flight.arrival_time if flight else "08:15",
        flight_date=str(flight.flight_date) if (flight and flight.flight_date) else "2026-08-01",
        seat_number=booking.seat_number or "1A",
        seat_class=seat.seat_class if seat else "Economy",
        gate_no=flight.gate_no if flight else "G1",
        terminal_no=flight.terminal_no if flight else "T3",
        total_amount=booking.total_amount or 5000.0,
        payment_method=payment.payment_method if payment else "UPI",
        transaction_id=payment.transaction_id if payment else "TXN-88992211",
        booking_status=booking.booking_status or "Confirmed",
        baggage_allowance=getattr(booking, 'baggage_allowance', '7kg Cabin + 15kg Check-in') or "7kg Cabin + 15kg Check-in",
        trip_type=getattr(booking, 'trip_type', 'One-Way') or "One-Way",
        ticket_url=f"http://localhost:8000/api/bookings/{booking.booking_id}/pdf",
    )

    # 1. Store in tickets directory
    tickets_dir = Path(__file__).resolve().parent.parent.parent / "tickets"
    tickets_dir.mkdir(parents=True, exist_ok=True)

    file_name = f"Ticket_{pnr}.pdf"
    file_path = str(tickets_dir / file_name)
    rel_path = f"tickets/{file_name}"

    with open(file_path, "wb") as f:
        f.write(pdf_bytes)

    # 2. Persist in SQL Database (tickets table)
    existing_ticket = db.query(Ticket).filter(Ticket.booking_id == booking.booking_id).first()
    if existing_ticket:
        existing_ticket.file_path = rel_path
        existing_ticket.pdf_data = pdf_bytes
    else:
        ticket_rec = Ticket(
            booking_id=booking.booking_id,
            file_path=rel_path,
            pdf_data=pdf_bytes,
        )
        db.add(ticket_rec)
    db.commit()

    return pdf_bytes


@router.get("/{booking_id}/pdf")
def download_ticket_pdf(booking_id: int, db: Session = Depends(get_db)):
    """Generate, save to DB and tickets folder, and return ticket PDF."""
    from fastapi.responses import Response

    booking = db.query(Booking).filter(Booking.booking_id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    pdf_bytes = generate_and_save_ticket(booking, db)

    filename = f"SkyBooker_BoardingPass_{booking.pnr}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename={filename}"},
    )


@router.get("/{booking_id}", response_model=BookingResponse)
def get_booking(booking_id: int, db: Session = Depends(get_db)):
    """Get a single booking."""
    booking = db.query(Booking).filter(Booking.booking_id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return _build_booking_response(booking, db)



@router.put("/{booking_id}/cancel", response_model=BookingResponse)
def cancel_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Cancel a booking and release the seat."""
    booking = db.query(Booking).filter(Booking.booking_id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    if booking.booking_status == "Cancelled":
        raise HTTPException(status_code=400, detail="Booking is already cancelled")

    # Only the booking owner or an admin can cancel
    if booking.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to cancel this booking")

    booking.booking_status = "Cancelled"
    booking.cancelled_at = datetime.now(timezone.utc)
    booking.refund_status = "pending"

    # Release the seat
    if booking.seat_id:
        seat = db.query(Seat).filter(Seat.seat_id == booking.seat_id).first()
        if seat:
            seat.is_booked = False

    # Restore available seats
    flight = db.query(Flight).filter(Flight.flight_id == booking.flight_id).first()
    if flight:
        flight.available_seats += 1

    # Update payment status
    payment = db.query(Payment).filter(Payment.booking_id == booking_id).first()
    if payment:
        payment.payment_status = "Refund Pending"

    db.commit()
    db.refresh(booking)
    return _build_booking_response(booking, db)


@router.post("/{booking_id}/checkin")
def checkin(booking_id: int, db: Session = Depends(get_db)):
    """Check-in a passenger for their flight."""
    booking = db.query(Booking).filter(Booking.booking_id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    if booking.booking_status == "Cancelled":
        raise HTTPException(status_code=400, detail="Cannot check in a cancelled booking")

    existing = db.query(BoardingPass).filter(BoardingPass.booking_id == booking_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Already checked in")

    flight = db.query(Flight).filter(Flight.flight_id == booking.flight_id).first()
    boarding_number = f"BP-{uuid.uuid4().hex[:6].upper()}"

    bp = BoardingPass(
        booking_id=booking_id,
        boarding_number=boarding_number,
        gate_no=flight.gate_no or "G1",
    )
    db.add(bp)
    return {"message": "Check-in successful", "boarding_number": boarding_number, "gate": bp.gate_no}

