import numpy as np
import pandas as pd
import datetime as dt
from datetime import datetime

import sqlalchemy
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session

from flask import Flask, jsonify

#######################
# Database setup
#######################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()

Base.prepare(engine, reflect=True)

#save reference to each table
measurement = Base.classes.measurement
station  = Base.classes.station

session = Session(engine)

#Flask setup

app = Flask(__name__)

#Flask routes endpoints

@app.route('/')

def welcome():
    return(
        f"<h1>Welcome to the Hawaii Climate Analysis API! <br/></h1>"
        f"<h2>Available endpoints: </br></h2>"
        f"/api/v1.0/precipitation</br>"
        f"/api/v1.0/stations</br>"
        f"/api/v1.0/tobs</br>"
        f"/api/v1.0/temp/start/end</br>"
        
        f"<h3>Page Links:</h3>"
        f"<ol><li><a href=http://127.0.0.1:5000/api/v1.0/precipitation>"
        f"Precipitation last year (JSON)</a></li><br/><br/>"
        f"<li><a href=http://127.0.0.1:5000/api/v1.0/stations>"
        f"Stations and their codes</a></li><br/><br/>"
        f"<li><a href=http://127.0.0.1:5000/api/v1.0/tobs>"
        f"Temperatures of most active station over last year (JSON)</a></li><br/><br/>"
        f"<li><a href=http://127.0.0.1:5000/api/v1.0/temp/2017-08-23>"
        f"Min, Avg, and Max since Start date (default is 8/23/17, change in URL to update data) </a></li><br/><br/>"
        f"<li><a href=http://127.0.0.1:5000/api/v1.0/temp/2016-08-23/2017-08-23>"
        f"Min, Avg, and Max between two dates (default is 8/23/16 - 8/23/17, change in URL to update data)</a></li></ol><br/>"
    )
    

@app.route("/api/v1.0/precipitation")
def precipitation():
    
    #return the precipitation data from last year
    #py = dt.date(2017,8,23) - dt.timedelta(days=365)
    latest1 = session.query(func.max(measurement.date)).scalar()  #latest date from database
    latest = datetime.strptime(latest1, '%Y-%m-%d')
    py = latest - dt.timedelta(days=365)
    py_date = py.strftime('%Y-%m-%d')
    
    #query for the date and precipitation for the last year
    precipitation = session.query(measurement.date, measurement.prcp).\
        filter(measurement.date>=py_date).all()
        
    precip = {date: prcp for date, prcp in precipitation}
    
    session.close()
    
    return jsonify(precip)

@app.route("/api/v1.0/stations")
def stations():
# session = Session(engine)
    results = session.query(station.station,station.name).all()
    
    #stations = list(np.ravel(results))
    
    stations = {station: name for station, name in results}
    
    session.close()
    
    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def temp_monthly():
    #session = Session(engine)
    #py = dt.date(2017,8,23) - dt.timedelta(days=365)
    #getting latest date from database
    latest1 = session.query(func.max(measurement.date)).scalar()  #latest date from database
    latest = datetime.strptime(latest1, '%Y-%m-%d')
    pyd = latest - dt.timedelta(days=365)
    py = pyd.strftime('%Y-%m-%d')
    
    #getting most active station id
    sel = [station.station, station.name, func.count(measurement.station)]
    s = session.query(*sel).filter(station.station == measurement.station).group_by(station.station).order_by(func.count(measurement.station).desc()).all()
    sdf = pd.DataFrame(s, columns=['station','name','count'])
    sdf.set_index('station',inplace=True)
    
    results = session.query(measurement.date,measurement.tobs).filter(measurement.station == sdf.index[0]).filter(measurement.date>py).all()
        
    #temps = list(np.ravel(results))
    temps = {date: prcp for date, prcp in results}
    
    session.close()
    
    return jsonify(temps)

@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start = None, end = None):
    #session = Session(engine)
    sel = [func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)]
    
    if not end:
        results = session.query(*sel).filter(measurement.date>=start).all()
        
        temps = list(np.ravel(results))
        return jsonify(temps)
    results = session.query(*sel).filter(measurement.date >= start).filter(measurement.date<=end).all()
    
    temps = list(np.ravel(results))
    
    session.close()
    
    return jsonify(temps)



if __name__ == '__main__':
    app.run(debug=True)
    
    




