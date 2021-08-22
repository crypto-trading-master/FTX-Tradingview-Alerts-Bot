import json
import os
import ftx

from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
# from pprint import pprint
from dotenv import load_dotenv
from datetime import datetime

app = Flask(__name__)

load_dotenv()

private_key = os.getenv("PRIVATE_KEY")
api_key = os.getenv("API_KEY")
api_secret = os.getenv("API_SECRET")
subaccount_name = os.getenv("SUBACCOUNT_NAME")

with open('config.json', 'r') as f:
    config = json.load(f)

client = ftx.FtxClient(api_key=api_key, api_secret=api_secret, subaccount_name=subaccount_name)

#  startBalance = config['startBalance']

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("SQLALCHEMY_DATABASE_URI")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Alert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    strategy = db.Column(db.String(100))
    ticker = db.Column(db.String(20))
    interval = db.Column(db.Integer)
    action = db.Column(db.String(10))
    chartTime = db.Column(db.DateTime)
    time = db.Column(db.DateTime)
    chartPrice = db.Column(db.Numeric)
    price = db.Column(db.Numeric)
    
    def __init__(self, strategy, ticker, interval, action, chartTime, time, chartPrice, price):
        self.strategy = strategy
        self.ticker = ticker
        self.interval = interval
        self.action = action
        self.chartTime = chartTime
        self.time = time
        self.chartPrice = chartPrice
        self.price = price

db.create_all()

@ app.route('/webhook', methods=['POST'])
def webhook():

    data = json.loads(request.data)

    if data['key'] != private_key:
        return {
            "status": "Private key error. Not authorized !"
        }

    strategy = data["strategy"]
    ticker = data["ticker"]
    action = data["action"]
    
    # TODO Convert JSON Datetime to MySQL Datetime
    
    chartTime = data["time"],
    interval = data["interval"],
    chartPrice = data["price"]
    
    time = datetime.now()
    
    market = client.get_market(ticker)

    bid = market["bid"]
    ask = market["ask"]
    
    if action == 'buy':
        price = ask
    else:
        price = bid
    
    alert = Alert(strategy, ticker, interval, action, chartTime, time, chartPrice, price)
    
    db.session.add(alert)
    db.session.commit()

    return {
        "code": "success"
    }


@ app.route('/alerts')
def alertsStatus():

    

    return {
        "alerts": "alerts"
    }
