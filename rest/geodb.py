#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from urllib2 import urlopen
import csv

from models.offices import Offices
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from sqlalchemy import event, create_engine, MetaData

from geoalchemy import WKTSpatialElement
from geoalchemy.functions import functions

# Using a Memory Database in Multiple Threads
# http://docs.sqlalchemy.org/en/rel_0_7/dialects/sqlite.html#using-a-memory-database-in-multiple-threads

engine = create_engine(
    'sqlite://',
    connect_args={'check_same_thread':False},
    poolclass=StaticPool
)

# this enables the libspatialite extension on each connection
@event.listens_for(engine, "connect")
def connect(dbapi_connection, notused):
    logging.info ("Loading Spatialite Ext!!")
    dbapi_connection.enable_load_extension(True)
    dbapi_connection.execute("SELECT load_extension('libspatialite.so');")


def init_db():

    logging.info ("Downloading data!!")
    myreq = urlopen("https://storage.googleapis.com/ymedlop-memory-db-demo/mocks/oficinas.csv").read()

    logging.info ("Initializating the application!!")

    engine.execute("SELECT InitSpatialMetaData();")

    session = sessionmaker(bind=engine)()

    logging.info("Creating Table Offices")
    Offices.__table__.create(engine)

    logging.info("Loading values in Offices file")
    data = csv.reader(myreq.splitlines(), delimiter=',')

    logging.info("Mapping values in Offices")

    for item in data:

        if item[2] == "" or item[2] == "":

            logging.info("Coords problem %s" % item)

        else:

            office = Offices(
                desc=item[0],
                address=item[1].decode('utf-8'),
                location='POINT({0} {1})'.format(item[2], item[3]),
                lat=float(item[2]),
                lng=float(item[3])
            )
            session.add(office)

    logging.info("Inserting values in Offices")
    session.commit()


def get_all():

    session = sessionmaker(bind=engine)()

    list = []

    # TODO: https://marshmallow.readthedocs.org/en/latest/nesting.html
    for office in session.query(Offices).order_by(Offices.location):
        list.append({
            "id": office.id,
            "desc": office.desc,
            "address": office.address,
            "latitude": office.lat,
            "longitude": office.lng
        })

    return list


def near(lat, lng, distance):

    list = []
    point = WKTSpatialElement('POINT({0} {1})'.format(lat, lng))

    logging.info("Doing search with %s" % 'POINT({0} {1})'.format(lat, lng))
    logging.info("And distance %s" % distance)

    session = sessionmaker(bind=engine)()
    query = session.query(Offices).filter(functions._within_distance(Offices.location, point, distance)).order_by(Offices.location)

    # TODO: https://marshmallow.readthedocs.org/en/latest/nesting.html
    for office in query:
        list.append({
            "id": office.id,
            "desc": office.desc,
            "address": office.address,
            "latitude": office.lat,
            "longitude": office.lng
        })

    return list
