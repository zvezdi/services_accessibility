from sqlalchemy import Column, Integer, String, Table
from geoalchemy2 import Geometry
from .base import Base

class School(Base):
    __table__ = Table(
        'schools',
        Base.metadata,
        Column('gid', Integer, primary_key=True),
        Column('subgroup_i', String),
        Column('geom', Geometry('MULTIPOINT')),
        schema='raw'
    )