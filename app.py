import json
import ftx  # type: ignore
import os
import datetime
from flask import Flask, request, g
# from pprint import pprint
from dotenv import load_dotenv

app = Flask(__name__)

with app.app_context():

    load_dotenv()

    api_key = os.getenv("API_KEY")
    api_secret = os.getenv("API_SECRET")
    subaccount_name = os.getenv("SUBACCOUNT_NAME")
    g.private_key = os.getenv("PRIVATE_KEY")

    with open('config.json', 'r') as f:
        config = json.load(f)

    startBalance = config['startBalance']
    g.currBalance = config['startBalance']
    risk = config['risk']
    fees = config['fees']
    leverage = config['leverage']

    client = ftx.FtxClient(api_key=api_key, api_secret=api_secret, subaccount_name=subaccount_name)

    g.positions = []  # type: list
    g.trades = []  # type: list
    g.alerts = []  # type: list

    print(g.currBalance)


    @ app.route('/webhook', methods=['POST'])
    def webhook():

        print(g.private_key)

        data = json.loads(request.data)

        if data['key'] != private_key:
            return {
                "status": "Private key error. Not authorized !"
            }

        ticker = data["ticker"]
        action = data["action"]

        alert = {}
        alert["datetime"] = datetime.datetime.now()
        alert["ticker"] = ticker
        alert["action"] = action
        g.alerts.append(alert)

        openPosition = True

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

                previousBalance = g.currBalance
                g.currBalance += profit

                profitPercent = (g.currBalance / previousBalance - 1) * leverage * 100

                g.positions.pop(0)

                trade["price"] = price
                trade["previousBalance"] = previousBalance
                trade["feesAmount"] = feesAmount
                trade["closeReturn"] = closeReturn
                trade["profit"] = profit
                trade["profitPercent"] = profitPercent
                trade["currentBalance"] = g.currBalance

                g.trades.append(trade)

            else:
                openPosition = False

        # Open position

        if openPosition:

            if action == 'buy':
                price = ask
            else:
                price = bid

            buyBalance = g.currBalance * risk
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
            g.positions.append(position)

        return {
            "code": "success"
        }


    @ app.route('/status')
    def status():

        return {
            "Start balance": startBalance,
            "Current balance": g.currBalance,
            "Number of trades": len(g.trades),
            "Number of positions": len(g.positions),
            "Number of alerts": len(g.alerts)
        }


    @ app.route('/trades')
    def tradeStatus():

        return {
            "trades": g.trades
        }


    @ app.route('/positions')
    def postionsStatus():

        return {
            "positions": g.positions
        }


    @ app.route('/alerts')
    def alertsStatus():

        return {
            "alerts": g.alerts
        }
