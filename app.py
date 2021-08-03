import json
from flask import Flask, request, jsonify
app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route('/webhook', methods=['POST'])
def webhook():

    data = json.loads(request.data)

    print(data["ticker"])
    print(data["bar"])

    return {
        "code": "succcess",
        "message": data
    }
