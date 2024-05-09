from flask import Flask, render_template, jsonify
from flask_restful import Api
from analyze import WCI_and_TEU, FBX_and_TEU, BDI_and_Cargo, stock_and_TEU_and_cargo, export_value_and_stock
from dotenv import load_dotenv
from map import geo_json


import pandas as pd
import os
import json
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
    graph1 = WCI_and_TEU()
    graph2 = FBX_and_TEU()
    graph3 = BDI_and_Cargo()
    graph4, graph5 = stock_and_TEU_and_cargo()
    graph6= export_value_and_stock()
    return render_template('marine.html', grafana_api_token=grafana_api_token, graph1=graph1, graph2=graph2,
                           graph3=graph3, graph4=graph4, graph5=graph5, graph6=graph6)


@app.route("/map")
def map():
    # ships_geojson = geo_json()
    #
    # ship_map(ships_geojson)
    return render_template("map.html")

#
@app.route("/api/port")
def port():

    ships_geojson = geo_json()
    return jsonify(ships_geojson)

@app.route("/api/boat")
def boat():
    boat_data = 'data/boat1yr.json'
    with open(boat_data, 'r') as file:
        monthly_boat = json.load(file)
    return jsonify(monthly_boat)


# @app.after_request
# def set_csp(response):
#     response.headers['Content-Security-Policy'] = "frame-ancestors 'self' http://13.237.180.170:3000/"
#     return response


if __name__ == '__main__':
    app.run(debug=True)
