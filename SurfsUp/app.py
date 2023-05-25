# Import the dependencies.

import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)
Base.classes.keys()
# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station
# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

# Precipitation data route
@app.route("/api/v1.0/precipitation")

def precipitation():
    session = Session(engine)

    """Return precipitation data of most recent year"""

    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date>="2016-08-23").all()

    session.close()

    # Create a dictionary from the data using "date" as the key and "prcp" as the value
    year_temps = []
    for date, prcp in results:
        temps_dict = {}
        temps_dict["date"] = date
        temps_dict["precipitation"] = prcp
        year_temps.append(temps_dict)

    return jsonify(year_temps)

# Station names route -- dictionary list of all unique stations and their names
@app.route("/api/v1.0/stations")

def stations():
    """Return a JSON list of all stations"""
    # Query all stations
    results = session.query(Station.name).all()

    # Convert list of tuples into normal list
    station_names = list(np.ravel(results))

    return jsonify(station_names)


# Temperature observation route -- dates and temps of the most active station for most recent year of data
@app.route("/api/v1.0/tobs")

def tobs():
    """Return a JSON list of Temperature Observations for the last year"""
    # Query all tobs between 2016-08-23 and 2017-08-23
    tobs_results = session.query(Measurement.tobs).filter(Measurement.station == 'USC00519281').filter(Measurement.date.between('2016-08-23', '2017-08-23')).all()

    # Convert list of tuples into normal list
    all_tobs = list(np.ravel(tobs_results))

    return jsonify(all_tobs)


# Start range route -- minimum, average, and maximum temperature from given start date until most recent date
@app.route("/api/v1.0/<start>")
def tobs_start(start):
    """Return TMIN, TAVE, and TMAX for all dates greater than or equal to start date"""

    # Query the database to get the maximum date
    max_date_query = session.query(func.max(Measurement.date)).scalar()

    # Convert max_date to proper date format
    max_date = dt.datetime.strptime(max_date_query, '%Y-%m-%d').date()

    # Query all tobs greater than and equal to startDate
    minAveMaxTobs =  session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= max_date).all()

    # Convert list of tuples into normal list
    minAveMaxTobsList = list(np.ravel(minAveMaxTobs))
    
    tmin = minAveMaxTobsList[0]
    tave = minAveMaxTobsList[1]
    tmax = minAveMaxTobsList[2]

    return jsonify(tmin, tave, tmax)


# Start/End range route -- minimum, average, and maximum temperature from given start date until given end date
@app.route("/api/v1.0/<start>/<end>")
def tobs_start_end(start, end):
    """Return TMIN, TAVE, and TMAX for dates from the start date to the end date, inclusive"""

    # Query all tobs between startDate and endDate inclusive
    summ_tobs = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()

    # Convert list of tuples into normal list
    summ_tobs_list = list(np.ravel(summ_tobs))

    tmin = summ_tobs_list[0]
    tave = summ_tobs_list[1]
    tmax = summ_tobs_list[2]

    return jsonify(tmin, tave, tmax)

if __name__ == '__main__':
    app.run(debug=True)
