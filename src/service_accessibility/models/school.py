from sqlalchemy import Column, Integer, String, Table
from sqlalchemy.ext.declarative import declarative_base
from geoalchemy2 import Geometry

Base = declarative_base()

class School(Base):
    __table__ = Table(
        'schools',
        Base.metadata,
        Column('gid', Integer, primary_key=True),
        Column('subgroup_i', String),
        Column('geom', Geometry('MULTIPOINT')),
        schema='raw'
    )