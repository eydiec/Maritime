from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from dotenv import load_dotenv
from datetime import datetime
import json
import logging
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()
url = os.getenv('INFLUX_URL')
org = os.getenv('INFLUX_ORG')
token = os.getenv('INFLUX_TOKEN')
bucket = os.getenv('INFLUX_BUCKET')

client = InfluxDBClient(token=token, url=url, org=org, timeout=90000)
write_api = client.write_api(write_options=SYNCHRONOUS, timeout=900000)
query_api = client.query_api()


def query_cordinate(port):
    query_cordinate = f"""
            from(bucket: "personal_project")
                |> range(start: -1y)
                |> filter(fn: (r) => r._measurement == "port_data" )
                |> filter(fn: (r) => r.portname == "{port}")
                |> filter(fn: (r) => r._field == "latitude" or r._field == "longitude")
                |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
                |> keep(columns: ["portname", "latitude", "longitude"])
                        """
    try:
        coordinates = query_api.query(query_cordinate)
        for coordinate in coordinates:
            for record in coordinate.records:
                latitude = record['latitude']
                longitude = record['longitude']
                if latitude and longitude:
                    # print(latitude, longitude)
                    return latitude, longitude
        # logging.error(f"No coordinate data found for port: {port}")
    except Exception as e:
        logging.error(f"Failed to query coordinates for port {port}: {e}")

    return None, None


def query_ship():
    start_time = datetime.now()
    ships = {
        'arriving': {},
        'departing': {}
    }
    query_arriving_ships = """
                    from(bucket: "personal_project")
                      |> range(start: -1y)
                      |> filter(fn: (r) => r._measurement == "進出口船舶" and r.purpose == "進港")
                      |> filter(fn: (r) => r["_field"] == "count")
                      |> keep(columns: ["_time", "_value", "port", "origin_port"])
                      |> aggregateWindow(every: 1mo, fn: sum, createEmpty: false)
                      |> yield(name: "sum")
                    """
    query_departing_ships = """
                    from(bucket: "personal_project")
                      |> range(start: -1y)
                      |> filter(fn: (r) => r._measurement == "進出口船舶" and r.purpose == "出港")
                      |> filter(fn: (r) => r["_field"] == "count")
                      |> keep(columns: ["_time", "_value", "port", "destination_port"])
                      |> aggregateWindow(every: 1mo, fn: sum, createEmpty: false)
                      |> yield(name: "sum")
                    """
    arriving_ships = query_api.query(query_arriving_ships)
    a_num = 0
    for arriving_ship in arriving_ships:
        for record in arriving_ship.records:
            end = record['port']
            start = record['origin_port']
            time = record['_time'].strftime('%Y-%m-%d')
            count = record['_value']
            # print(end,start)

            aend_latitude, aend_longitude = query_cordinate(end)
            astart_latitude, astart_longitude = query_cordinate(start)
            if aend_latitude is not None and astart_latitude is not None:
                pair = (time, start, end)
                if pair in ships['arriving']:
                    ships['arriving']['count'] += count
                else:

                    ships['arriving'][pair] = {'time': time, 'start': start, 'start_latitude': astart_latitude,
                                               'start_longitude': astart_longitude, 'end': end,
                                               'end_latitude': aend_latitude, 'end_longitude': aend_longitude,
                                               'count': count}
                    a_num += 1
                    # print(a_num) # 1year: 3508, 1 month: 323

    departing_ships = query_api.query(query_departing_ships)
    d_num = 0
    for departing_ship in departing_ships:
        for record in departing_ship.records:
            end = record['destination_port']
            start = record['port']
            time = record['_time'].strftime('%Y-%m-%d')
            count = record['_value']
            bend_latitude, bend_longitude = query_cordinate(end)
            bstart_latitude, bstart_longitude = query_cordinate(start)
            if bend_latitude is not None and bstart_latitude is not None:
                pair = (time, start, end)
                if pair in ships['departing']:
                    ships['departing']['count'] += count
                else:
                    ships['departing'][pair] = {'time': time, 'start': start, 'start_latitude': bstart_latitude,
                                                'start_longitude': bstart_longitude, 'end': end,
                                                'end_latitude': bend_latitude, 'end_longitude': bend_longitude,
                                                'count': count}
                    d_num += 1

    end_time = datetime.now()
    print(a_num)
    print(d_num)
    procee_time = end_time - start_time
    print(procee_time)
    return ships


def geo_json():
    ships = query_ship()
    geojson = {
        'type': 'FeatureCollection',
        'features': []
    }

    for status, ship_list in ships.items():
        if status == 'arriving':
            for key, value in ship_list.items():
                geojson['features'].append({
                    'type': 'Feature',
                    'properties': {
                        'status': status,
                        'time': value['time'],
                        'start_port': value['start'],
                        'end_port': value['end'],
                        'count': value['count']
                    },
                    'geometry': {
                        'type': 'Point',
                        'coordinates': [value['start_longitude'], value['start_latitude']]
                    }
                })
        else:
            for key, value in ship_list.items():
                geojson['features'].append({
                    'type': 'Feature',
                    'properties': {
                        'status': status,
                        'time': value['time'],
                        'start_port': value['start'],
                        'end_port': value['end'],
                        'count': value['count']
                    },
                    'geometry': {
                        'type': 'Point',
                        'coordinates': [value['end_longitude'], value['end_latitude']]
                    }
                })
    ship_geodata = 'data/ship1yr.json'
    with open(ship_geodata, 'w') as file:
        json.dump(geojson, file, indent=4)
    print(geojson)
    return geojson


def boat_json():
    start_time = datetime.now()
    boat_type = {
        'arriving': {},
        'departing': {}
    }
    query_boat_type = """
    from(bucket: "personal_project")
      |> range(start: -1y)
      |> filter(fn: (r) => r._measurement == "進出口船舶" )
      |> filter(fn: (r) => r["purpose"] == "出港" or r["purpose"] == "進港")
      |> keep(columns: ["_time", "_value", "purpose", "boat_type"])
      |> aggregateWindow(every: 1mo, fn: sum, createEmpty: false)
      |> yield(name: "sum")
    """
    query_boats = query_api.query(query_boat_type)
    end_time = datetime.now()
    for boats in query_boats:
        for record in boats.records:
            # print(record)
            purpose = record.values.get('purpose', None)
            purpose_key = 'arriving' if purpose == '進港' else 'departing'
            time = record.get_time().strftime('%Y-%m-%d')
            count = record.get_value()
            original_boat = record.values.get('boat_type', "Others")

            # classify boat types
            if "貨櫃" in original_boat:
                boat = "Container"
            elif "雜貨" in original_boat or "散裝" in original_boat:
                boat = "Dry Bulk"
            elif "客船" in original_boat or "遊艇" in original_boat:
                boat = "Passenger"
            else:
                boat = "Others"

            print(time, purpose_key, boat, count)
            if time not in boat_type[purpose_key]:
                boat_type[purpose_key][time] = {}
            if boat in boat_type[purpose_key][time]:
                boat_type[purpose_key][time][boat] += count
            else:
                boat_type[purpose_key][time][boat] = count

    boat_data = 'data/boat1yr.json'
    with open(boat_data, 'w') as file:
        json.dump(boat_type, file, indent=4)
    print(boat_type)
    return boat_type


boat_json()
