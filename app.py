import json
import ftx  # type: ignore
import os
import datetime
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

    global currBalance

    data = json.loads(request.data)

    if data['key'] != private_key:
        return {
            "status": "Private key error. Not authorized !"
        }

    openPosition = True

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

            trade = {}
            trade["ticker"] = ticker
            trade["datetime"] = datetime.datetime.now()
            trade["action"] = action
            trade["leverage"] = leverage
            trade["position"] = position

            feesAmount = coinAmount * price * fees
            closeReturn = coinAmount * price - feesAmount

            if action == 'buy':
                profit = positionCost - closeReturn
            else:
                profit = closeReturn - positionCost

            previousBalance = currBalance
            currBalance += profit

            profitPercent = (currBalance / previousBalance - 1) * leverage * 100

            positions.pop(0)

            # TO DO ## trade Dict must be detailed with position prices and balances

            trade["price"] = price
            trade["previousBalance"] = previousBalance
            trade["feesAmount"] = feesAmount
            trade["closeReturn"] = closeReturn
            trade["profit"] = profit
            trade["profitPercent"] = profitPercent
            trade["currentBalance"] = currBalance

            trades.append(trade)

        else:
            openPosition = False

    # Open position

    if openPosition:

        if action == 'buy':
            price = ask
        else:
            price = bid

        buyBalance = currBalance * risk
        feesAmount = buyBalance * leverage * fees
        coinAmount = (buyBalance * leverage - feesAmount) / price
        positionCost = buyBalance * leverage

        position = {}
        position["ticker"] = ticker
        position["action"] = action
        position["buyBalance"] = buyBalance
        position["feesAmount"] = feesAmount
        position["coinAmount"] = coinAmount
        position["price"] = price
        position["positionCost"] = positionCost
        positions.append(position)

    return {
        "code": "success"
    }


@ app.route('/status')
def status():
    return {
        "Current balance": currBalance,
        "Number of trades": len(trades),
        "Number of positions": len(positions)
    }


@ app.route('/trades')
def tradeStatus():
    return {
        "trades": trades
    }


@ app.route('/positions')
def psotionsStatus():
    return {
        "positions": positions
    }
