from flask import Flask, request, jsonify

from dotenv import load_dotenv, find_dotenv

import os

load_dotenv(find_dotenv())

HOST = "127.0.0.1"
PORT = 8000

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY")

logic_endpoint = None

def init(callback):
    global logic_endpoint
    logic_endpoint = callback
    return app

@app.route("/", methods = ["POST"])
def only_endpoint():
    if request.method == "POST":
        query = request.get_json()["query"]

        result = logic_endpoint(query)

        return jsonify({"result": result})