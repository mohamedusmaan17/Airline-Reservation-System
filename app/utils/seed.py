"""Seed the database with sample data for demo purposes."""
from datetime import date

from sqlalchemy.orm import Session

from app.models.airline import Airline
from app.models.airport import Airport
from app.models.flight import Flight
from app.models.passenger import Passenger
from app.models.user import User
from app.services.auth_service import hash_password


def seed_database(db: Session):
    """Populate DB with sample airlines, airports, flights, passengers, and admin user."""

    # Skip if already seeded
    if db.query(User).first():
        return

    # ── Admin user ─────────────────────────────────────
    admin = User(
        username="admin",
        email="admin@airline.com",
        password_hash=hash_password("admin123"),
        role="admin",
    )
    db.add(admin)

    # ── Demo customer ──────────────────────────────────
    customer = User(
        username="john",
        email="john@example.com",
        password_hash=hash_password("john123"),
        role="customer",
    )
    db.add(customer)

    # ── Airlines ───────────────────────────────────────
    airlines_data = [
        ("Air India", "AI", "New Delhi", "+91 11 2462 2220"),
        ("IndiGo", "6E", "Gurugram", "+91 124 435 2500"),
        ("SpiceJet", "SG", "Gurugram", "+91 987 180 3333"),
        ("Vistara", "UK", "Gurugram", "+91 928 922 8888"),
        ("Go First", "G8", "Mumbai", "+91 22 7117 3773"),
    ]
    airlines = []
    for name, code, hq, contact in airlines_data:
        a = Airline(airline_name=name, airline_code=code, headquarters=hq, contact_number=contact)
        db.add(a)
        airlines.append(a)

    db.flush()  # Get IDs

    # ── Airports ───────────────────────────────────────
    airports_data = [
        ("Indira Gandhi International Airport", "DEL", "New Delhi", "India"),
        ("Chhatrapati Shivaji International Airport", "BOM", "Mumbai", "India"),
        ("Kempegowda International Airport", "BLR", "Bangalore", "India"),
        ("Rajiv Gandhi International Airport", "HYD", "Hyderabad", "India"),
        ("Chennai International Airport", "MAA", "Chennai", "India"),
        ("Netaji Subhas Chandra Bose Airport", "CCU", "Kolkata", "India"),
        ("Cochin International Airport", "COK", "Kochi", "India"),
        ("Sardar Vallabhbhai Patel Airport", "AMD", "Ahmedabad", "India"),
    ]
    airports = []
    for name, code, city, country in airports_data:
        ap = Airport(airport_name=name, airport_code=code, city=city, country=country)
        db.add(ap)
        airports.append(ap)

    db.flush()

    # ── Flights ────────────────────────────────────────
    flights_data = [
        (airlines[0].airline_id, airports[0].airport_id, airports[1].airport_id, "AI101", "06:00", "08:15", "05:30", date(2026, 8, 1), 180, 5500, "Scheduled", "A12", "T3"),
        (airlines[0].airline_id, airports[1].airport_id, airports[0].airport_id, "AI102", "10:30", "12:45", "10:00", date(2026, 8, 1), 180, 5800, "Scheduled", "B5", "T2"),
        (airlines[1].airline_id, airports[0].airport_id, airports[2].airport_id, "6E301", "07:45", "10:30", "07:15", date(2026, 8, 1), 180, 4200, "Scheduled", "C8", "T1"),
        (airlines[1].airline_id, airports[2].airport_id, airports[3].airport_id, "6E455", "14:00", "15:15", "13:30", date(2026, 8, 2), 180, 3500, "Scheduled", "D3", "T1"),
        (airlines[2].airline_id, airports[0].airport_id, airports[4].airport_id, "SG201", "09:00", "11:45", "08:30", date(2026, 8, 2), 180, 3800, "Scheduled", "A7", "T2"),
        (airlines[3].airline_id, airports[1].airport_id, airports[2].airport_id, "UK831", "16:30", "18:00", "16:00", date(2026, 8, 3), 180, 6200, "Scheduled", "B2", "T2"),
        (airlines[3].airline_id, airports[0].airport_id, airports[5].airport_id, "UK771", "11:00", "13:30", "10:30", date(2026, 8, 3), 180, 5900, "Scheduled", "C1", "T3"),
        (airlines[0].airline_id, airports[0].airport_id, airports[6].airport_id, "AI505", "20:00", "23:00", "19:30", date(2026, 8, 4), 180, 7200, "Scheduled", "A3", "T3"),
    ]

    from app.models.seat import Seat

    for fd in flights_data:
        f = Flight(
            airline_id=fd[0], source_airport=fd[1], destination_airport=fd[2],
            flight_number=fd[3], departure_time=fd[4], arrival_time=fd[5],
            boarding_time=fd[6], flight_date=fd[7], total_seats=fd[8],
            available_seats=fd[8], ticket_price=fd[9], flight_status=fd[10],
            gate_no=fd[11], terminal_no=fd[12],
        )
        db.add(f)
        db.flush()

        # Generate seats for each flight
        letters = ["A", "B", "C", "D", "E", "F"]
        seat_types = ["window", "middle", "aisle", "aisle", "middle", "window"]
        rows_needed = (f.total_seats + 5) // 6
        business_rows = min(3, rows_needed)

        for r in range(1, rows_needed + 1):
            for c_idx, letter in enumerate(letters):
                seat_class = "business" if r <= business_rows else "economy"
                price_addon = 1500.0 if seat_class == "business" else (
                    300.0 if seat_types[c_idx] == "window" else 0.0
                )
                seat = Seat(
                    flight_id=f.flight_id,
                    seat_number=f"{r}{letter}",
                    seat_class=seat_class,
                    seat_type=seat_types[c_idx],
                    price_addon=price_addon,
                )
                db.add(seat)

    # ── Passengers ─────────────────────────────────────
    passengers_data = [
        ("Mohamed", "Usmaan", "Male", date(2000, 5, 15), "+91 9876543210", "usmaan@gmail.com", "P1234567", "India"),
        ("Priya", "Sharma", "Female", date(1995, 8, 22), "+91 9876543211", "priya@gmail.com", "P2345678", "India"),
        ("Rahul", "Kumar", "Male", date(1992, 3, 10), "+91 9876543212", "rahul@gmail.com", "P3456789", "India"),
        ("Aisha", "Khan", "Female", date(1998, 11, 5), "+91 9876543213", "aisha@gmail.com", "P4567890", "India"),
        ("Vijay", "Patel", "Male", date(1990, 7, 18), "+91 9876543214", "vijay@gmail.com", "P5678901", "India"),
    ]
    passengers = []
    for first, last, gender, dob, phone, email, passport, nationality in passengers_data:
        p = Passenger(
            first_name=first, last_name=last, gender=gender,
            date_of_birth=dob, phone=phone, email=email,
            passport_number=passport, nationality=nationality,
        )
        db.add(p)
        passengers.append(p)

    db.flush()

    # ── Sample Bookings & Payments ──────────────────────
    import uuid

    from app.models.booking import Booking
    from app.models.payment import Payment
    from app.models.review import Review

    all_flights = db.query(Flight).all()
    if all_flights and len(passengers) >= 3:
        b1 = Booking(
            user_id=customer.id,
            passenger_id=passengers[0].passenger_id,
            flight_id=all_flights[0].flight_id,
            seat_number="1A",
            booking_status="Confirmed",
            total_amount=7000.0,
            pnr="SK" + uuid.uuid4().hex[:6].upper(),
        )
        b2 = Booking(
            user_id=customer.id,
            passenger_id=passengers[1].passenger_id,
            flight_id=all_flights[2].flight_id,
            seat_number="4F",
            booking_status="Confirmed",
            total_amount=4500.0,
            pnr="SK" + uuid.uuid4().hex[:6].upper(),
        )
        b3 = Booking(
            user_id=customer.id,
            passenger_id=passengers[2].passenger_id,
            flight_id=all_flights[1].flight_id,
            seat_number="12C",
            booking_status="Cancelled",
            total_amount=5800.0,
            refund_status="refunded",
            pnr="SK" + uuid.uuid4().hex[:6].upper(),
        )
        db.add_all([b1, b2, b3])
        db.flush()

        p1 = Payment(booking_id=b1.booking_id, amount=7000.0, payment_method="UPI", payment_status="Success", transaction_id="TXN-99881122")
        p2 = Payment(booking_id=b2.booking_id, amount=4500.0, payment_method="CREDIT_CARD", payment_status="Success", transaction_id="TXN-44556677")
        p3 = Payment(booking_id=b3.booking_id, amount=5800.0, payment_method="UPI", payment_status="Refunded", transaction_id="TXN-11223344")
        db.add_all([p1, p2, p3])

    # ── Sample Customer Reviews ─────────────────────────
    sample_reviews = [
        ("Amazing flight! Boarding was extremely fast, cabin staff were polite and helpful.", 5, "positive", 0.95, all_flights[0].flight_id if all_flights else None),
        ("Smooth flight from Delhi to Bangalore. Punctual departure and clean seats.", 5, "positive", 0.92, all_flights[2].flight_id if all_flights else None),
        ("Slight delay of 25 minutes due to weather, but overall good experience.", 4, "neutral", 0.65, all_flights[1].flight_id if all_flights else None),
        ("Comfortable business class seats with extra legroom. Worth the upgrade!", 5, "positive", 0.98, all_flights[0].flight_id if all_flights else None),
        ("Great customer support when rescheduling my ticket. Highly recommended!", 5, "positive", 0.89, all_flights[3].flight_id if len(all_flights) > 3 else None),
    ]

    for text, rating, sentiment, score, f_id in sample_reviews:
        rev = Review(
            user_id=customer.id,
            flight_id=f_id,
            rating=rating,
            review_text=text,
            sentiment=sentiment,
            sentiment_score=score,
        )
        db.add(rev)

    db.commit()
    print("[+] Database seeded with sample data, bookings, payments, and reviews")
    print("   Admin login: admin / admin123")
    print("   Customer login: john / john123")

