from sqlalchemy import Column, Integer, String, Table
from geoalchemy2 import Geometry
from .base import Base

class PointOfInterest(Base):
    __abstract__ = True
    gid = Column(Integer, primary_key=True)
    subgroup_i = Column(String)
    geom = Column(Geometry('MULTIPOINT'))

class CulturePOI(PointOfInterest):
    __tablename__ = 'culture'
    __table_args__ = {'schema': 'raw'}

class HealthPOI(PointOfInterest):
    __tablename__ = 'health'
    __table_args__ = {'schema': 'raw'}

class KidsPOI(PointOfInterest):
    __tablename__ = 'kids'
    __table_args__ = {'schema': 'raw'}

class MobilityPOI(PointOfInterest):
    __tablename__ = 'mobility'
    __table_args__ = {'schema': 'raw'}

class SchoolPOI(PointOfInterest):
    __tablename__ = 'schools'
    __table_args__ = {'schema': 'raw'}

class ServicePOI(PointOfInterest):
    __tablename__ = 'other_pois'
    __table_args__ = {'schema': 'raw'}

class GreenPOI(PointOfInterest):
    __tablename__ = 'parks_gardens_entr'
    __table_args__ = {'schema': 'raw'}

class SportPOI(PointOfInterest):
    __tablename__ = 'sport'
    __table_args__ = {'schema': 'raw'}
