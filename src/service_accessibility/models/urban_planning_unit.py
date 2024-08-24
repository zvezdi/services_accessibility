from sqlalchemy import Column, Integer, String, Table
from geoalchemy2 import Geometry
from .base import Base

class UrbanPlanningUnit(Base):
    __table__ = Table(
        'urban_planning_units',
        Base.metadata,
        Column('gid', Integer, primary_key=True),
        Column('regname', String),
        Column('rajon', String),
        Column('geom', Geometry('MULTIPOLYGON')),
        schema='raw'
    )
