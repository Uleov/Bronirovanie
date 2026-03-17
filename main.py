import sys

from sqlalchemy import text

from app.db import SessionLocal
from app.models import create_all
from app.services.booking_service import (
    book_place,
    cancel_booking,
    list_places_with_status,
    seed_demo_data,
)


def cmd_init_db() -> None:
    create_all()
    print("ok")


def cmd_seed() -> None:
    with SessionLocal() as session:
        seed_demo_data(session)
        session.commit()
    print("ok")


def cmd_list_places(session_id: int) -> None:
    with SessionLocal() as session:
        rows = list_places_with_status(session, session_id=session_id)
    for row in rows:
        status = "booked" if row["booking_id"] else "free"
        print(f'{row["place_id"]}\t{row["place_name"]}\t{status}')


def cmd_book(session_id: int, place_id: int, user_id: int) -> None:
    with SessionLocal() as session:
        booking_id = book_place(
            session,
            session_id=session_id,
            place_id=place_id,
            user_id=user_id,
        )
        session.commit()
    print(booking_id)


def cmd_cancel(booking_id: int, user_id: int) -> None:
    with SessionLocal() as session:
        cancel_booking(session, booking_id=booking_id, user_id=user_id)
        session.commit()
    print("ok")


def cmd_report() -> None:
    with SessionLocal() as session:
        stmt = text(
            """
            SELECT
              s.id AS session_id,
              s.starts_at AS starts_at,
              COUNT(b.id) AS booked
            FROM sessions s
            LEFT JOIN bookings b ON b.session_id = s.id
            GROUP BY s.id, s.starts_at
            ORDER BY s.id
            """
        )
        rows = session.execute(stmt).mappings().all()
    for row in rows:
        print(f'{row["session_id"]}\t{row["starts_at"]}\t{row["booked"]}')


def usage() -> str:
    return "\n".join(
        [
            "python main.py init-db",
            "python main.py seed",
            "python main.py list-places <session_id>",
            "python main.py book <session_id> <place_id> <user_id>",
            "python main.py cancel <booking_id> <user_id>",
            "python main.py report",
        ]
    )


def main(argv: list[str]) -> None:
    if len(argv) < 2:
        print(usage(), file=sys.stderr)
        raise SystemExit(2)
    cmd = argv[1]
    try:
        if cmd == "init-db":
            cmd_init_db()
            return
        if cmd == "seed":
            cmd_seed()
            return
        if cmd == "list-places":
            if len(argv) != 3:
                print(usage(), file=sys.stderr)
                raise SystemExit(2)
            cmd_list_places(int(argv[2]))
            return
        if cmd == "book":
            if len(argv) != 5:
                print(usage(), file=sys.stderr)
                raise SystemExit(2)
            cmd_book(int(argv[2]), int(argv[3]), int(argv[4]))
            return
        if cmd == "cancel":
            if len(argv) != 4:
                print(usage(), file=sys.stderr)
                raise SystemExit(2)
            cmd_cancel(int(argv[2]), int(argv[3]))
            return
        if cmd == "report":
            cmd_report()
            return
        print(usage(), file=sys.stderr)
        raise SystemExit(2)
    except ValueError as e:
        print(str(e), file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main(sys.argv)
