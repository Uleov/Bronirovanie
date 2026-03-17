import os
import sys
from pathlib import Path

from alembic import context
from sqlalchemy import create_engine

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.models.base import Base
import app.models.entities  # noqa: F401

config = context.config
target_metadata = Base.metadata

db_url = os.environ.get("DATABASE_URL") or config.get_main_option("sqlalchemy.url")

engine = create_engine(db_url)

with engine.connect() as connection:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()
