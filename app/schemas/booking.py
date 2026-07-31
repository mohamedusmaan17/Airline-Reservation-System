from datetime import datetime

from pydantic import BaseModel


class BookingCreate(BaseModel):
    passenger_id: int
    flight_id: int
    seat_id: int
    payment_method: str | None = "UPI"
    baggage_allowance: str | None = "7kg Cabin + 15kg Check-in"
    trip_type: str | None = "One-Way"


class BookingResponse(BaseModel):
    booking_id: int
    pnr: str
    passenger_name: str | None = None
    flight_number: str | None = None
    seat_number: str | None = None
    booking_date: datetime | None = None
    booking_status: str
    total_amount: float
    refund_status: str | None = None
    baggage_allowance: str | None = None
    trip_type: str | None = None

    class Config:
        from_attributes = True



class PassengerCreate(BaseModel):
    first_name: str
    last_name: str
    gender: str | None = None
    date_of_birth: str | None = None
    phone: str | None = None
    email: str | None = None
    passport_number: str | None = None
    nationality: str | None = None


class PassengerResponse(BaseModel):
    passenger_id: int
    first_name: str
    last_name: str
    gender: str | None = None
    date_of_birth: str | None = None
    phone: str | None = None
    email: str | None = None
    passport_number: str | None = None
    nationality: str | None = None

    class Config:
        from_attributes = True


class PaymentResponse(BaseModel):
    payment_id: int
    booking_id: int
    amount: float
    payment_method: str | None = None
    payment_date: datetime | None = None
    payment_status: str
    transaction_id: str | None = None

    class Config:
        from_attributes = True
