import datetime as dt

from sqlalchemy import Select, exists, literal, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.entities import Booking, EventSession, Place, User
from app.repositories.booking_repo import get_booking_by_id


def seed_demo_data(session: Session) -> None:
    has_users = session.execute(select(exists().where(User.id != None))).scalar_one()
    if not has_users:
        session.add_all([User(name="alice"), User(name="bob")])

    has_places = session.execute(select(exists().where(Place.id != None))).scalar_one()
    if not has_places:
        session.add_all([Place(name="A1"), Place(name="A2"), Place(name="A3")])

    has_sessions = session.execute(select(exists().where(EventSession.id != None))).scalar_one()
    if not has_sessions:
        now = dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
        session.add_all(
            [
                EventSession(event_id=1, starts_at=now + dt.timedelta(hours=2)),
                EventSession(event_id=1, starts_at=now + dt.timedelta(days=1, hours=2)),
            ]
        )


def book_place(session: Session, session_id: int, place_id: int, user_id: int) -> int:
    s_exists = session.execute(select(exists().where(EventSession.id == session_id))).scalar_one()
    if not s_exists:
        raise ValueError("session_not_found")

    p_exists = session.execute(select(exists().where(Place.id == place_id))).scalar_one()
    if not p_exists:
        raise ValueError("place_not_found")

    u_exists = session.execute(select(exists().where(User.id == user_id))).scalar_one()
    if not u_exists:
        raise ValueError("user_not_found")

    booking = Booking(session_id=session_id, place_id=place_id, user_id=user_id)
    session.add(booking)
    try:
        session.flush()
    except IntegrityError:
        session.rollback()
        raise ValueError("already_booked")
    return booking.id


def cancel_booking(session: Session, booking_id: int, user_id: int) -> None:
    booking = get_booking_by_id(session, booking_id)
    if not booking:
        raise ValueError("booking_not_found")
    if booking.user_id != user_id:
        raise ValueError("not_owner")
    session.delete(booking)


def list_places_with_status(session: Session, session_id: int) -> list[dict]:
    stmt: Select[tuple[int, str, int | None]] = (
        select(
            Place.id.label("place_id"),
            Place.name.label("place_name"),
            Booking.id.label("booking_id"),
        )
        .select_from(Place)
        .outerjoin(
            Booking,
            (Booking.place_id == Place.id) & (Booking.session_id == literal(session_id)),
        )
        .order_by(Place.id)
    )
    return [dict(row) for row in session.execute(stmt).mappings().all()]

