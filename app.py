from flask import Flask, render_template, jsonify, make_response
from flask_restful import Api
from analyze import InfluxDataHandler, plot_pair
from dotenv import load_dotenv
from map import geo_json
import os
import json
import logging

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
api = Api(app)
app.secret_key = os.getenv('SECRET_KEY')


@app.route("/")
def home():
    grafana_api_token = os.getenv('GRAFANA_TOKEN')

    handler = InfluxDataHandler()
    query_wci = handler.generate_query(index="WCI")
    query_fbx = handler.generate_query(index="FBX")
    query_bdi = handler.generate_query(index="BDI")
    query_stock = handler.generate_query(index="台股航運指數")
    query_export = handler.generate_query(index="TW_ExportValue")
    query_container = handler.generate_query(measurement="貨櫃裝卸量", field="TEU")
    query_cargo = handler.generate_query(measurement="貨物裝卸量", field="charge_ton")

    graph1 = plot_pair(handler, query_wci, query_container, 'WCI vs. Container Throughput', 'WCI',
                       'Container Throughput')
    graph2 = plot_pair(handler, query_fbx, query_container, 'FBX vs. Container Throughput', 'FBX',
                       'Container Throughput')
    graph3 = plot_pair(handler, query_bdi, query_cargo, 'BDI vs. Cargo Throughput', 'BDI', 'Cargo Throughput')
    graph4 = plot_pair(handler, query_stock, query_container, 'Stock Index vs. Container Throughput', 'Stock Index',
                       'Container Throughput')
    graph5 = plot_pair(handler, query_stock, query_cargo, 'Stock Index vs. Cargo Throughput', 'Stock Index',
                       'Cargo Throughput')
    graph6 = plot_pair(handler, query_stock, query_export, 'Stock Index vs. Export Value', 'Stock Index',
                       'Export Value')

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
    if 'type' not in ships_geojson or ships_geojson['type'] != 'FeatureCollection' or 'features' not in ships_geojson:
        return make_response(jsonify({"error": "Invalid data format"}), 500)
    return jsonify(ships_geojson)


@app.route("/api/boat")
def boat():
    try:
        boat_data = 'data/boat1yr.json'
        with open(boat_data, 'r') as file:
            monthly_boat = json.load(file)
            if not monthly_boat:  # Check for empty data
                return make_response(jsonify({"error": "Data is empty"}), 500)
        return jsonify(monthly_boat)
    except FileNotFoundError:
        return make_response(jsonify({"error": "File not found"}), 404)
    except json.JSONDecodeError:
        return make_response(jsonify({"error": "Invalid JSON format"}), 500)


if __name__ == '__main__':
    app.run(debug=True)
