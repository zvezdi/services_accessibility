from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from geoalchemy2 import load_spatialite
from ..config import DATABASE_URL

def get_db_engine():
    return create_engine(DATABASE_URL, echo=True)

def get_db_session():
    engine = get_db_engine()
    Session = sessionmaker(bind=engine)
    return Session()