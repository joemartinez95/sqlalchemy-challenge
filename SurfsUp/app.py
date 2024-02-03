# Import the dependencies.
from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import numpy as np
import pandas as pd
import datetime as dt
#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# # reflect an existing database into a new model
Base = automap_base()

# # reflect the tables
Base.prepare(autoload_with=engine)

# # Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

# # Create our session (link) from Python to the DB
session = Session(engine)

# #################################################
# # Flask Setup
# #################################################
app = Flask(__name__)



# #################################################
# # Flask Routes
# #################################################
@app.route('/')
def welcome():
    return(
        f'Welcome to the Climate API!<br/>'
        f'Available Routes:<br/>'
        f'/api/v1.0/precipitation<br/>'
        f'/api/v1.0/stations<br/>'
        f'/api/v1.0/tobs<br/>'
        f'/api/v1.0/<start><br/>'
        f'/api/v1.0/<start>/<end>'
    )

@app.route('/api/v1.0/precipitation')
def rain():
    session = Session(engine)
    one_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    results = session.query(measurement.date, measurement.prcp).filter(measurement.date >= one_year).all()
    rows = [{'Date': result[0], 'Precipitation': result[1]} for result in results]

    return jsonify(rows)



@app.route('/api/v1.0/stations')
def stations():
    session = Session(engine)
    results = session.query(station.station).all()
    session.close()
    all_stations = list(np.ravel(results))

    return jsonify(all_stations)


@app.route('/api/v1.0/tobs')
def tobs():
    session = Session(engine)
    new_one_year = dt.date(2017, 8, 18) - dt.timedelta(days=365)
    station_results = session.query(measurement.tobs).filter(measurement.date >= new_one_year).filter(measurement.station == 'USC00519281').all()
    new_rows = [{'Temperature': result[0]} for result in station_results]

    return jsonify(new_rows)

@app.route('/api/v1.0/<start>')
def date_info(start):
    max_date = session.query(func.max(measurement.date)).scalar()
    min_date = session.query(func.min(measurement.date)).scalar()
    start_date = dt.datetime.strptime(start, '%Y-%m-%d').date()
    results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).filter(measurement.date >= start_date).all()
    if start > max_date or start < min_date:
         return jsonify({'error': 'No data found for the given start date'})
    else:
        if results:
             min_temp, avg_temp, max_temp = results[0]
             result_dict = {
                'start_date': start_date.strftime('%Y-%m-%d'),
                'min_temperature': min_temp,
                'avg_temperature': avg_temp,
                'max_temperature': max_temp
            }
             return jsonify(result_dict)
   


@app.route('/api/v1.0/<start>/<end>')
def date_info2(start, end):
    max_date = session.query(func.max(measurement.date)).scalar()
    min_date = session.query(func.min(measurement.date)).scalar()
    start_date = dt.datetime.strptime(start, '%Y-%m-%d').date()
    end_date = dt.datetime.strptime(end, '%Y-%m-%d').date()
    results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).filter(measurement.date >= start_date, measurement.date <= end_date).all()
    if end < min_date:
         return jsonify({'error': 'No data found for the given date range'})
    else:
        if results:
            min_temp, avg_temp, max_temp = results[0]
            result_dict2 = {
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d'),
                'min_temperature': min_temp,
                'avg_temperature': avg_temp,
                'max_temperature': max_temp
            }
            return jsonify(result_dict2), 200, {'Content-Type': 'application/json; charset=utf-8', 'indent': 2}

if __name__ == '__main__':
    app.run()