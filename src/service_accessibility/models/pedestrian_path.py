from sqlalchemy import Column, Integer, String, Float
from geoalchemy2 import Geometry
from .base import Base

class PedestrianPath(Base):
    __tablename__ = 'pedestrian_network'
    __table_args__ = {'schema': 'raw'}

    id = Column(Integer, primary_key=True)
    name = Column(String)
    type = Column(String)
    max_speed = Column(Float)
    length_m = Column(Float)
    minutes = Column(Float)
    adm_ter = Column(Integer)
    geom = Column(Geometry('GEOMETRY'))  # Can be LINESTRING or MULTILINESTRING
