import json
import os

from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
# from pprint import pprint
from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv()

private_key = os.getenv("PRIVATE_KEY")

with open('config.json', 'r') as f:
    config = json.load(f)

#  startBalance = config['startBalance']

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("SQLALCHEMY_DATABASE_URI")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

@ app.route('/webhook', methods=['POST'])
def webhook():

    data = json.loads(request.data)

    if data['key'] != private_key:
        return {
            "status": "Private key error. Not authorized !"
        }

    ticker = data["ticker"]
    action = data["action"]
    time = data["time"],
    interval = data["interval"],
    chartPrice = data["price"]


    return {
        "code": "success"
    }


@ app.route('/alerts')
def alertsStatus():

    

    return {
        "alerts": "alerts"
    }
