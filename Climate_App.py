#imports
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from datetime import datetime, timedelta
from flask import Flask, jsonify

############################################################
##database setup
#create engine
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station
# Create our session (link) from Python to the DB
session = Session(engine)
############################################################

#create app
app = Flask(__name__)

@app.route('/')
def welcome():
    return (
        f'Welcome to my Climate API!<br/>'
        f'<br/>'
        f'Available Routes:<br/>'
        f'/api/v1.0/precipitation<br/>'
        f'/api/v1.0/stations<br/>'
        f'/api/v1.0/tobs<br/>'
        f'/api/v1.0/insert-start-date-for-temp <br/>'
        f'/api/v1.0/insert-start-date-for-temp/insert-end-date-for-temp<br/>'
    )
@app.route('/api/v1.0/precipitation')
def precipitation():
    #query date and precip amount
    results = session.query(Measurement.date, Measurement.prcp).\
    order_by(Measurement.date.desc())

    #create dictionary for data and append to list
    precip_analysis = []
    for precip in results:
        date_precip = {}
        date_precip['date'] = precip.date
        date_precip['prcp'] = precip.prcp
        precip_analysis.append(date_precip)

    return jsonify(precip_analysis)

@app.route('/api/v1.0/stations')
def stations():
    #query and count number of stations
    station_id = session.query(Station.station).all()

    return jsonify(station_id)

@app.route('/api/v1.0/tobs')
def temp():
    #query to get most active station
    active = session.query(Measurement.station, func.count(Measurement.station)).\
            group_by(Measurement.station).order_by(func.count(Measurement.station).desc())
    #get station of highest observations
    highest = list(active[0])
    high_obs = highest[0]

    #query to get last date with data
    results = session.query(Measurement.date).\
            order_by(Measurement.date.desc())

    #get max date
    max_date = list(results[0])
    max_date = max_date[0]
    
    #get year month day of max
    max_datetime = datetime.strptime(max_date, '%Y-%m-%d')
    # subtract one year
    one_year = max_datetime - timedelta(days=365)
    #collect year month day of one year previous to max
    one_year = datetime.strftime(one_year, '%Y-%m-%d')

    #query for last 12 months of data given
    temp_data = session.query(Measurement.date, Measurement.tobs).\
                    filter(Measurement.date > one_year).\
                    filter(Measurement.station == high_obs).\
                    order_by(Measurement.date).all()

    return jsonify(temp_data)
@app.route('/api/v1.0/<start>')
def calc_temp(start):

    #convert start to datetime
    start = datetime.strptime(start, '%Y-%m-%d').date()

    #query to get temp data from start to end of data
    temp_data = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                group_by(Measurement.date).filter(Measurement.date >= start).all()
    
    #check length of temp data
    if len(temp_data) != 0:

        #if there is data return it
        return jsonify(temp_data)
    
    #if there is no data send error
    else:
        return jsonify({'error': f'Start date {start} not found.'}), 404

@app.route('/api/v1.0/<start>/<end>')
def range_temp(start, end):

    #convert start to datetime
    start = datetime.strptime(start, '%Y-%m-%d').date()

    #convert end to datetime
    end = datetime.strptime(end, '%Y-%m-%d').date()

    #query to get temp data between two dates
    temp_data_between = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                group_by(Measurement.date).filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    #check length of temp data
    if len(temp_data_between) != 0:

        #if there is data return it
        return jsonify(temp_data_between)

    #if there is no data send error
    else:
        return jsonify({'error': f'Start date {start} not found.'}), 404

if __name__ == '__main__':
    app.run(debug=True)
