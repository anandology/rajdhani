"""
Module to interact with the database.
"""
from sqlalchemy import (
    create_engine, MetaData, Table,
    select, func, and_, or_, literal)
from . import placeholders
from . import config
from . import db_ops

db_ops.ensure_db()

engine = create_engine(config.db_uri, echo=True)
meta = MetaData(bind=engine)

train_table = Table("train", meta, autoload=True)
station_table = Table("station", meta, autoload=True)

def search_stations(q):
    """Returns the top ten stations matching the given query string.

    This is used to get show the auto complete on the home page.

    The q is the few characters of the station name or
    code entered by the user.
    """
    # return placeholders.AUTOCOMPLETE_STATIONS
    s = station_table

    query = (
        select(s.c.code, s.c.name)
        .where(
            or_(
                func.upper(s.c.code)==q.upper(),
                func.upper(s.c.name).contains(q.upper())))
        .limit(10)
    )
    return [dict(row) for row in query.execute()]

def get_timeslot(value):
    """Converts the timeslot value to begin time and end time.
    """
    slots = {
        "1": ("00:00", "07:59"),
        "2": ("08:00", "11:59"),
        "3": ("12:00", "15:59"),
        "4": ("16:00", "19:59"),
        "5": ("20:00", "23:59"),
    }
    return slots[value]

def apply_slot_filter(column, timeslot):
    begin_time, end_time = get_timeslot(timeslot)
    return and_(column >= begin_time, column <= end_time)

def apply_slot_filters(q, column, timeslots):
    if not timeslots:
        return q

    clause = or_(*[apply_slot_filter(column, timeslot) for timeslot in timeslots])
    return q.where(clause)

def search_trains(
        from_station_code,
        to_station_code,
        ticket_class=None,
        departure_time=[],
        arrival_time=[]):
    """Returns all the trains that source to destination stations on
    the given date. When ticket_class is provided, this should return
    only the trains that have that ticket class.

    This is used to get show the trains on the search results page.
    """
    t = train_table
    q = (select(
            t.c.number,
            t.c.name,
            t.c.from_station_code,
            t.c.from_station_name,
            t.c.to_station_code,
            t.c.to_station_name,
            t.c.departure,
            t.c.arrival,
            t.c.duration_h,
            t.c.duration_m)
        .where(t.c.from_station_code==from_station_code)
        .where(t.c.to_station_code==to_station_code))
    if ticket_class:
        columns = {
            "SL": t.c.sleeper,
            "3A": t.c.third_ac,
            "2A": t.c.second_ac,
            "1A": t.c.first_ac,
            "FC": t.c.first_class,
            "CC": t.c.chair_car,
        }
        q = q.where(columns[ticket_class]==1)

    q = apply_slot_filters(q, t.c.departure, departure_time)
    q = apply_slot_filters(q, t.c.arrival, arrival_time)

    return q.execute().all()

    # TODO: make a db query to get the matching trains
    # and replace the following dummy implementation

    return [
        {
            "train_number": "12028",
            "train_name": "Shatabdi Exp",
            "from_station_code": "SBC",
            "from_station_name": "Bangalore",
            "to_station_code": "MAS",
            "to_station_name": "Chennai",
            "start_date": date,
            "start_time": "06:00",
            "end_date":  date,
            "end_time": "11:00",
            "duration": "05:00"
        },
        {
            "train_number": "12608",
            "train_name": "Lalbagh Exp",
            "from_station_code": "SBC",
            "from_station_name": "Bangalore",
            "to_station_code": "MAS",
            "to_station_name": "Chennai",
            "start_date": date,
            "start_time": "06:20",
            "end_date":  date,
            "end_time": "12:15",
            "duration": "05:55"
        },
    ]
