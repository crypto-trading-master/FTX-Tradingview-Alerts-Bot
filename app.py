import json
import os

from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
# from pprint import pprint
from dotenv import load_dotenv
from datetime import datetime

app = Flask(__name__)

load_dotenv()

private_key = os.getenv("PRIVATE_KEY")

with open('config.json', 'r') as f:
    config = json.load(f)

#  startBalance = config['startBalance']

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("SQLALCHEMY_DATABASE_URI")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class alert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.String(20))
    interval = db.Column(db.Integer)
    action = db.Column(db.String(10))
    chartTime = db.Column(db.DateTime)
    time = db.Column(db.DateTime)
    chartPrice = db.Column(db.Numeric)
    price = db.Column(db.Numeric)
    
    def __init__(self, ticker, interval, action, chartTime, time, chartPrice, price):
        self.ticker = ticker
        self.interval = interval
        self.action = action
        self.chartTime = chartTime
        self.time = time
        self.chartPrice = chartPrice
        self.price = price


@ app.route('/webhook', methods=['POST'])
def webhook():

    data = json.loads(request.data)

    if data['key'] != private_key:
        return {
            "status": "Private key error. Not authorized !"
        }

    ticker = data["ticker"]
    action = data["action"]
    chartTime = data["time"],
    interval = data["interval"],
    chartPrice = data["price"]
    
    time = datetime.now()
    
    # TODO Get current price from FTX

    currAlert = alert(ticker, interval, action, chartTime, time, chartPrice, price)
    

    return {
        "code": "success"
    }


@ app.route('/alerts')
def alertsStatus():

    

    return {
        "alerts": "alerts"
    }
