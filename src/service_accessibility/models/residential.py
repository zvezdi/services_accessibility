from sqlalchemy import Column, Integer, String, Table
from geoalchemy2 import Geometry
from .base import Base

class Residential(Base):
    __table__ = Table(
        'buildings_all_residential_2024',
        Base.metadata,
        Column('gid', Integer, primary_key=True),
        Column('floorcount', Integer),
        Column('appcount', Integer),
        Column('geom', Geometry('MULTIPOLYGON')),
        schema='raw'
    )