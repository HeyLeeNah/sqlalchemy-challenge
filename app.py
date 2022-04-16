#Imports
#from sys import last_traceback, last_type
from flask import Flask, jsonify
import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

#Database setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect = True)
Measurement = Base.classes.measurement
Station = Base.classes.station
session = Session(engine)

#Create an app, being sure to pass __name__
app = Flask(__name__)



@app.route("/")
def home():
    #Debugging on the server
    print("Server received request for 'Home' page...")

    #Response back to the client
    return (
        f"Welcome to my Honolulu, Hawaii! Check out the climate!<br/><br/>"
        f"All the available routes:<br/><br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/startend<br/>"
        
        )

@app.route("/api/v1.0/precipitation")
def precipitation():
    print("Server received request for 'Precipitation' page...")
    
    # Query all the precipitation measurements
    prcp = session.query(Measurement.date, Measurement.prcp).all()

    # List of dictionaries with all the precipitation measurements
    dict = []
    for x in prcp:
        dict.append(x._asdict())
    
    return jsonify(dict)


@app.route("/api/v1.0/stations")
def stations():
    print("Server received request for 'Stations' page...")

    # Query all the stations measurements
    stations = session.query(Station.station).all()

    # List of dictionaries with all the stations
    dict = []
    for x in stations:
        dict.append(x._asdict())

    return jsonify(dict)


@app.route("/api/v1.0/tobs")
def tobs():
    print("Server received request for 'Tobs' page...")

    # Query the dates and temperature observations of the most active station for the last year of data.
    
    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date = dt.date(2017,8, 23)
    year_ago = last_date - dt.timedelta(days=365)

    last_temp = session.query(Measurement.date, Measurement.tobs)\
        .filter(Measurement.station == "USC00519281").filter(Measurement.date >= year_ago).all()

    dict = []
    for x in last_temp:
        dict.append(x._asdict())

    return jsonify(dict)


@app.route("/api/v1.0/<start>")
def start(start):
    print("Server received request for 'Start' page...")

    start = dt.datetime(2011, 6, 2)

    sel = [Measurement.station, 
      func.min(Measurement.tobs),
      func.max(Measurement.tobs),
      func.avg(Measurement.tobs)]

    start_query = session.query(*sel).filter(Measurement.date >= start).all()
    start_list = [
        {"TMIN": start_filter[0][0]},
        {"TAVG": start_filter[0][1]},
        {"TMAX": start_filter[0][2]}]

    for x in start_query:
        if x >= start:
            return jsonify (start_list)
        else:
            return jsonify ("Request past given time interval.")


@app.route("/api/v1.0/<start>/<end>")
def startend(start,end):
    print("Server received request for 'StartEnd' page...")

    start = dt.datetime(2011, 6, 2)
    end = dt.datetime(2017,8,23)

    sel = [Measurement.station, 
      func.min(Measurement.tobs),
      func.max(Measurement.tobs),
      func.avg(Measurement.tobs)]

    startend_query = session.query(*sel).filter(Measurement.date.between(start,end)).all()
    startend_list = [
        {"TMIN": start_filter[0][0]},
        {"TAVG": start_filter[0][1]},
        {"TMAX": start_filter[0][2]}]

    for x in startend_query:
        if (x >= start) and (x <= end):
            return jsonify (startend_list)
        else:
            return jsonify ("Request past given time interval.")

    


session.close()

if __name__ == "__main__":
    app.run(debug=True)
