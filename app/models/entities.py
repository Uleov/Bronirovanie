import datetime as dt

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)

    bookings: Mapped[list["Booking"]] = relationship(back_populates="user")


class Place(Base):
    __tablename__ = "places"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)

    bookings: Mapped[list["Booking"]] = relationship(back_populates="place")


class EventSession(Base):
    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[int | None] = mapped_column(nullable=True)
    starts_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    bookings: Mapped[list["Booking"]] = relationship(back_populates="session")


class Booking(Base):
    __tablename__ = "bookings"
    __table_args__ = (UniqueConstraint("session_id", "place_id", name="uq_booking_session_place"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    place_id: Mapped[int] = mapped_column(ForeignKey("places.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    session: Mapped[EventSession] = relationship(back_populates="bookings")
    place: Mapped[Place] = relationship(back_populates="bookings")
    user: Mapped[User] = relationship(back_populates="bookings")

