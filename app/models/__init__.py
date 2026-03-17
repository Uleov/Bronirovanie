from app.db import engine
from app.models.base import Base
from app.models.entities import Booking, EventSession, Place, User


def create_all() -> None:
    Base.metadata.create_all(engine)


__all__ = [
    "Base",
    "User",
    "Place",
    "EventSession",
    "Booking",
    "create_all",
]

