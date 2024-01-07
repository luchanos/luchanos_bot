from contextlib import contextmanager

from sqlalchemy import create_engine, Column, Integer, Text, DateTime, Sequence
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from logging import getLogger

logger = getLogger(__name__)
Base = declarative_base()


class Event(Base):
    __tablename__ = 'events'

    id = Column(Integer, primary_key=True)
    actual_date = Column(DateTime, default=datetime.utcnow)
    status = Column(Text)
    type = Column(Text)


engine = create_engine('postgresql://postgres:postgres@localhost:5433/postgres')

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)


@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = Session()
    try:
        yield session
        session.commit()
    except Exception as err:
        session.rollback()
        logger.error(err)
        raise err
    finally:
        session.close()
