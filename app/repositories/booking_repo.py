from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.models.entities import Booking


def get_booking_by_id(session: Session, booking_id: int) -> Booking | None:
    stmt: Select[tuple[Booking]] = select(Booking).where(Booking.id == booking_id)
    return session.execute(stmt).scalar_one_or_none()


def get_booking_for_place(session: Session, session_id: int, place_id: int) -> Booking | None:
    stmt: Select[tuple[Booking]] = select(Booking).where(
        Booking.session_id == session_id,
        Booking.place_id == place_id,
    )
    return session.execute(stmt).scalar_one_or_none()

