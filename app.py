import numpy as np
import datetime as dt
import pandas as pd

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

#save references for the tables
measurement = Base.classes.measurement
station  = Base.classes.station

#create our session link from Python to Database
session = Session(engine)

#Flask setup

app = Flask(__name__)

#Flask routes endpoints

print(Base.classes.keys())




