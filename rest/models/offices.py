# -*- coding: utf-8 -*-

from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from geoalchemy.spatialite import SQLiteComparator
from geoalchemy import (Geometry, GeometryColumn, GeometryDDL, Point)

Base = declarative_base()


class Offices(Base):
    __tablename__ = 'offices'
    id = Column(Integer, primary_key=True)
    desc = Column(String(255))
    address = Column(String(255))
    location = GeometryColumn(Point(2, srid=4326, spatial_index=True), comparator = SQLiteComparator)
    beautiful_location = Column(String(255))

GeometryDDL(Offices.__table__)
