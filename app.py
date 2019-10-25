# Python SQL toolkit and Object Relational Mapper
# import dependencies
import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, inspect, func
from flask import Flask, jsonify


######################
### Setup Database
######################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

######################
### Setup Flask
######################
# Create an app, passing __name__
app = Flask(__name__)

######################
### Flask Routes
######################
@app.route('/')
def index():
    return (
        f"Available Routes:<br/>"
        f"<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"<br/>"
        f"/api/v1.0/stations<br/>"
        f"<br/>"
        f"/api/v1.0/tobs<br/>"
        f"<br/>"
        f"/api/v1.0/start<br/>"
        f" 'When given start date (yyyy-mm-dd) returns min/avg/max temperature for all dates after or on date.'<br/>"
        f"<br/>"
        f"/api/v1.0/start/end<br/>"
        f" 'When given start and end date (yyyy-mm-dd), returns min/avg/max temperature for dates between them inclusive'<br/>"
    )


@app.route("/api/v1.0/precipitation")
def percipitation():
    """ Convert the query results to a Dictionary using date as the key
    and prcp as the value.
    Return the JSON representation of your dictionary. """

    session = Session(engine)
    # Perform a query to retrieve the data and precipitation scores
    results = session.query(Measurement.date, Measurement.prcp).all()
    session.close()

    # Create a dictionary from the prcp data and append to prcp_data
    prcp_data = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict[date] = prcp
        prcp_data.append(prcp_dict)

    return jsonify(prcp_data)


@app.route("/api/v1.0/stations")
def station():
    """Return a JSON list of stations from the dataset"""
    # Query to retrieve station data

    session = Session(engine)
    result = session.query(Station.station, Station.name).all()
    session.close()

    return jsonify(result)


@app.route("/api/v1.0/tobs")
def tobs():
    """query for the dates and temperature observations from a year
    from the last data point. Return a JSON list of Temperature Observations
    (tobs) for the previous year."""
    year_ago = find_date()

    # Query to retrieve the station, date, tobs
    session = Session(engine)
    results = session.query(Measurement.station, Measurement.date, Measurement.tobs)\
    .filter(Measurement.date > year_ago).all()
    session.close()

    # Create a dictionary from the results
    tobs_data = []
    for station, date, tobs in results:
        tobs_dict = {}
        tobs_dict[date] = (tobs, station)
        tobs_data.append(tobs_dict)

    return jsonify(tobs_data)


@app.route("/api/v1.0/<start>")
def find_tmps(start):
    """ Return a JSON list of the minimum temperature, the average temperature,
    and the max temperature for a given start or start-end range.
    When given the start only, calculate TMIN, TAVG, and TMAX for all dates
    greater than and equal to the start date."""
    # Query for the tmin tavg tmax greater after the given date
    session = Session(engine)
    result = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs),
            func.max(Measurement.tobs))\
            .filter(Measurement.date >= start).all()
    session.close()

    return jsonify(result)


@app.route("/api/v1.0/<start>/<end>")
def find_tmps2(start, end):
    """ Return a JSON list of the minimum temperature, the average temperature,
    and the max temperature for a given start or start-end range. """
    # Query for the tmin tavg tmax greater after the start date and before the end date
    session = Session(engine)
    result = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs),
            func.max(Measurement.tobs))\
            .filter(Measurement.date >= start)\
            .filter(Measurement.date <= end).all()
    session.close()

    return jsonify(result)


######################
### helper functions
######################
def find_date():
    """ Use DB to retieve a year ago from the last data point """
    # Calculate the date 1 year ago from the last data point in the database
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    # Change into a datetime obj
    date_last = dt.datetime.strptime(last_date[0], "%Y-%m-%d")
    # Calculate a year from last date
    year_ago = date_last - dt.timedelta(days=365)

    return year_ago

######################
### run Flask App
######################
if __name__ == '__main__':
    app.run(debug=True)
