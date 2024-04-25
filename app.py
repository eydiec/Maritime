from flask import Flask, request, render_template, make_response, redirect, url_for, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_restful import Api
from analyze import WCI_and_TEU, FBX_and_TEU, BDI_and_Cargo, stock_and_TEU_and_cargo
from dotenv import load_dotenv
from map import ship_map
import pandas as pd
import os
import datetime
import logging

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
api = Api(app)
app.secret_key = os.getenv('SECRET_KEY')


@app.route("/")
def home():
    grafana_api_token = os.getenv('GRAFANA_TOKEN')
    # logging.info(f"Using Grafana API Token: {grafana_api_token}")
    # graph1 = WCI_and_TEU()
    # graph2 = FBX_and_TEU()
    # graph3 = BDI_and_Cargo()
    # graph4, graph5 = stock_and_TEU_and_cargo()
    return render_template('marine.html', grafana_api_token=grafana_api_token)
    # , graph1=graph1, graph2=graph2,graph3=graph3, graph4=graph4, graph5=graph5)


@app.route("/map")
def map():
    ship_map()
    return render_template("map.html")
#
# @app.route("/api/port")
# def port():
#     ships = {
#         'arriving': {
#             'start': {'latitude': -20.0, 'longitude': 118.0},
#             'end': {'latitude': 22.5529, 'longitude': 120.2851}
#         },
#         'departing': {
#             'start': {'latitude': 35.0, 'longitude': 129.0},
#             'end': {'latitude': 22.5529, 'longitude': 120.2851}
#         }
#     }
#     return jsonify(ships)


# @app.route("/analyze")
# def analyze():
#
#     graph1 = WCI_and_TEU()
#     graph2 = FBX_and_TEU()
#     graph3 = BDI_and_Cargo()
#
#     return render_template('marine.html',graph1 = graph1, graph2 = graph2, graph3=graph3)


# @app.after_request
# def set_csp(response):
#     response.headers['Content-Security-Policy'] = "frame-ancestors 'self' http://13.237.180.170:3000/"
#     return response


if __name__ == '__main__':
    app.run(debug=True)
