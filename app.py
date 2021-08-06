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

currBalance = config['startBalance']
risk = config['risk']
fees = config['fees']
leverage = config['leverage']

client = ftx.FtxClient(api_key=api_key, api_secret=api_secret, subaccount_name=subaccount_name)

positions = []  # type: list
trades = []  # type: list

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

    ticker = data["ticker"]
    action = data["action"]

    result = client.get_market(ticker)

    bid = result["bid"]
    ask = result["ask"]

    if positions:
        position = positions[0]

        # Check position type

        positionAction = position["action"]

        if positionAction != action:
            # Close position

            if positionAction == 'buy':  # Sell
                price = bid
            else:  # positionAction == sell -> Buy
                price = ask

            coinAmount = position["coinAmount"]
            positionCost = position["positionCost"]

            feesAmount = coinAmount * price * fees
            closeReturn = coinAmount * price - feesAmount

            if positionAction == 'buy':
                profit = closeReturn - positionCost
            else:
                profit = positionCost - closeReturn

            previousBalance = currBalance
            currBalance += profit

            profitPercent = (currBalance / previousBalance - 1) * leverage * 100

            # #### TO DO  Create trade Dict and add to trades

    # Open position

    if action == 'buy':
        price = ask
    else:
        price = bid


@ app.route('/status')
def status():
    return {
        "Current balance": currBalance,
        "Number of trades": len(trades)
    }


@ app.route('/trades')
def tradeStatus():
    return {
        trades
    }
