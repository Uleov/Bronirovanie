import datetime as dt
import unittest

from sqlalchemy import create_engine, event, select
from sqlalchemy.orm import Session, sessionmaker

from app.models.base import Base
from app.models.entities import Booking, EventSession, Place, User
from app.services.booking_service import book_place, cancel_booking, list_places_with_status


def make_session() -> Session:
    engine = create_engine("sqlite:///:memory:")

    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_connection, connection_record) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
    return SessionLocal()


class BookingServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.session = make_session()
        self.user = User(name="alice")
        self.other_user = User(name="bob")
        self.place = Place(name="A1")
        self.event_session = EventSession(
            event_id=1,
            starts_at=dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=2),
        )
        self.session.add_all([self.user, self.other_user, self.place, self.event_session])
        self.session.commit()

    def tearDown(self) -> None:
        self.session.close()

    def test_book_place_creates_booking(self) -> None:
        booking_id = book_place(
            self.session,
            session_id=self.event_session.id,
            place_id=self.place.id,
            user_id=self.user.id,
        )
        self.session.commit()

        booking = self.session.get(Booking, booking_id)
        self.assertIsNotNone(booking)
        self.assertEqual(booking.user_id, self.user.id)

    def test_book_place_rejects_duplicate_place_for_same_session(self) -> None:
        book_place(
            self.session,
            session_id=self.event_session.id,
            place_id=self.place.id,
            user_id=self.user.id,
        )
        self.session.commit()

        with self.assertRaisesRegex(ValueError, "already_booked"):
            book_place(
                self.session,
                session_id=self.event_session.id,
                place_id=self.place.id,
                user_id=self.other_user.id,
            )

    def test_cancel_booking_rejects_non_owner(self) -> None:
        booking_id = book_place(
            self.session,
            session_id=self.event_session.id,
            place_id=self.place.id,
            user_id=self.user.id,
        )
        self.session.commit()

        with self.assertRaisesRegex(ValueError, "not_owner"):
            cancel_booking(self.session, booking_id=booking_id, user_id=self.other_user.id)

    def test_cancel_booking_removes_booking_for_owner(self) -> None:
        booking_id = book_place(
            self.session,
            session_id=self.event_session.id,
            place_id=self.place.id,
            user_id=self.user.id,
        )
        self.session.commit()

        cancel_booking(self.session, booking_id=booking_id, user_id=self.user.id)
        self.session.commit()

        booking = self.session.execute(select(Booking).where(Booking.id == booking_id)).scalar_one_or_none()
        self.assertIsNone(booking)

    def test_list_places_with_status_marks_booked_place(self) -> None:
        book_place(
            self.session,
            session_id=self.event_session.id,
            place_id=self.place.id,
            user_id=self.user.id,
        )
        self.session.commit()

        rows = list_places_with_status(self.session, session_id=self.event_session.id)

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["place_id"], self.place.id)
        self.assertIsNotNone(rows[0]["booking_id"])


if __name__ == "__main__":
    unittest.main()
