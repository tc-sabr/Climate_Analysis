#import sqlalchemy stuff
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

#import flask
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
    station_count = session.query(Station.station).all()

    return jsonify(station_count)

# @app.route('api/v1.0/tobs')
# def temp():
#     return "Joe"

if __name__ == '__main__':
    app.run(debug=True)
