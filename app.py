import json
import ftx  # type: ignore
import os
from flask import Flask, request
from pprint import pprint
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("API_KEY")
api_secret = os.getenv("API_SECRET")
subaccount_name = os.getenv("SUBACCOUNT_NAME")

client = ftx.FtxClient(api_key=api_key, api_secret=api_secret, subaccount_name=subaccount_name)

app = Flask(__name__)


@ app.route('/')
def hello_world():
    return 'Hello, World!'


@ app.route('/webhook', methods=['POST'])
def webhook():

    data = json.loads(request.data)

    action = data["action"]
    print('Action:', action)

    result = client.get_market('BTC-PERP')

    if action == 'buy':
        price = result['ask']
    else:
        price = result['bid']

    result = client.get_account_info()

    return {
        "code": "succcess",
        "price": price,
        "account info": result
    }
