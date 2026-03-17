## Booking (SQLAlchemy 2.x, SQLite)

### Setup

`python -m venv .venv`

Windows PowerShell:

`.\.venv\Scripts\Activate.ps1`

`pip install -r requirements.txt`

### Run

`python main.py init-db`

`python main.py seed`

`python main.py list-places 1`

`python main.py book 1 1 1`

`python main.py report`

### Alembic

`alembic upgrade head`
