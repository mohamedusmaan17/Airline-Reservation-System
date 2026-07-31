from datetime import date

from pydantic import BaseModel


class FlightSearch(BaseModel):
    source: str | None = None
    destination: str | None = None
    flight_date: date | None = None
    seat_class: str | None = None


class FlightCreate(BaseModel):
    airline_id: int
    source_airport: int
    destination_airport: int
    flight_number: str
    departure_time: str
    arrival_time: str
    boarding_time: str | None = None
    flight_date: date | None = None
    total_seats: int = 180
    ticket_price: float = 0.0
    flight_status: str = "Scheduled"
    gate_no: str | None = None
    terminal_no: str | None = None


class FlightUpdate(BaseModel):
    airline_id: int | None = None
    source_airport: int | None = None
    destination_airport: int | None = None
    flight_number: str | None = None
    departure_time: str | None = None
    arrival_time: str | None = None
    boarding_time: str | None = None
    flight_date: date | None = None
    total_seats: int | None = None
    ticket_price: float | None = None
    flight_status: str | None = None
    gate_no: str | None = None
    terminal_no: str | None = None


class FlightResponse(BaseModel):
    flight_id: int
    airline_name: str | None = None
    source_name: str | None = None
    destination_name: str | None = None
    flight_number: str
    departure_time: str
    arrival_time: str
    boarding_time: str | None = None
    flight_date: date | None = None
    total_seats: int
    available_seats: int
    ticket_price: float
    flight_status: str
    gate_no: str | None = None
    terminal_no: str | None = None

    class Config:
        from_attributes = True


class SeatResponse(BaseModel):
    seat_id: int
    seat_number: str
    seat_class: str
    seat_type: str
    is_booked: bool
    price_addon: float

    class Config:
        from_attributes = True
