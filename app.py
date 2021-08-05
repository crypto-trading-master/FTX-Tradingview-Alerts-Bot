import json
import ftx  # type: ignore
import os
from flask import Flask, request
# from pprint import pprint
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("API_KEY")
api_secret = os.getenv("API_SECRET")
subaccount_name = os.getenv("SUBACCOUNT_NAME")
private_key = os.getenv("PRIVATE_KEY")

with open('config.json', 'r') as f:
    config = json.load(f)

startBalance = config['startBalance']
risk = config['risk']

client = ftx.FtxClient(api_key=api_key, api_secret=api_secret, subaccount_name=subaccount_name)

positions = []  # type: list

app = Flask(__name__)


@ app.route('/')
def hello_world():
    return 'Hello, World!'


@ app.route('/webhook', methods=['POST'])
def webhook():

    data = json.loads(request.data)

    if data['key'] != private_key:
        return {
            "status": "Private key error. Not authorized !"
        }

    ticker = data['ticker']
    action = data["action"]

    result = client.get_market(ticker)

    if positions:

        position = positions[0]

        # Check position type

        positionAction = position["action"]

        if positionAction != action:

            # Close position

            if positionAction == 'buy':
                # Sell
                price = result['bid']
            else:
                # Buy
                price = result['ask']

    # Open position

    if action == 'buy':
        price = result['ask']
    else:
        price = result['bid']


@ app.route('/status')
def status():
    return {
        "currBalance": "10000"
    }
