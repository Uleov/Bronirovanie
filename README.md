## Бронирование мест.

Небольшой учебный проект - места, сеансы и брони. Ограничение - одно место можно забронировать только один раз в рамках одного сеанса (`UNIQUE(session_id, place_id)`).

### Установка.

`python -m venv .venv`

Windows PowerShell.

`.\.venv\Scripts\Activate.ps1`

`pip install -r requirements.txt`

### Запуск.

`python main.py init-db`

`python main.py seed`

`python main.py list-places <session_id>`

`python main.py book <session_id> <place_id> <user_id>`

`python main.py cancel <booking_id> <user_id>`

`python main.py report`

### Alembic.

Миграции нужны, чтобы поднимать/обновлять схему БД.

`alembic upgrade head`

Можно указать другую БД через переменную окружения

PowerShell:

`$env:DATABASE_URL="sqlite:///test.db"; alembic upgrade head`
