from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from dotenv import load_dotenv
import logging
import os
import json
import datetime
import pytz
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, WebDriverException


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()
url = os.getenv('INFLUX_URL')
org = os.getenv('INFLUX_ORG')
token = os.getenv('INFLUX_TOKEN')
bucket = os.getenv('INFLUX_BUCKET')

options = Options()
# options.add_argument('--headless')  # run in headless mode.
options.add_argument('--disable-gpu')  # disable GPU hardware acceleration.
options.add_argument('start-maximized')  # open the window at max size for the screen.
options.add_argument('disable-infobars')  # prevent Chrome from displaying
options.add_argument('--disable-extensions')  # disable all browser extensions.

# Connect to InfluxDB
try:
    client = InfluxDBClient(token=token, url=url, org=org, timeout=90000)
    write_api = client.write_api(write_options=SYNCHRONOUS, timeout=900000)
    query_api = client.query_api()
    logging.info("successfully connect to InfluxDB")
except Exception as e:
    logging.error('fail to connect with InfluxDB')


def get_port():
    query_origin_port = """
            from(bucket: "personal_project")
              |> range(start: -5y)
              |> filter(fn: (r) => r["_measurement"] == "進出口船舶")
              |> keep(columns: ["origin_port"])
              |> distinct(column: "origin_port")
            """
    query_destination_port = """
            from(bucket: "personal_project")
              |> range(start: -5y)
              |> filter(fn: (r) => r["_measurement"] == "進出口船舶")
              |> keep(columns: ["destination_port"])
              |> distinct(column: "destination_port")
            """
    query_port = """
            from(bucket: "personal_project")
              |> range(start: -5y)
              |> filter(fn: (r) => r["_measurement"] == "進出口船舶")
              |> keep(columns: ["port"])
              |> distinct(column: "port")
            """
    port_set = set()
    results_origin_port = query_api.query(query_origin_port)
    for table in results_origin_port:
        for record in table.records:
            port = record.values.get('origin_port')
            if port is not None and len(port) == 5 and port.isalpha():
                port_set.add(port)
    results_destination_port = query_api.query(query_destination_port)
    for table in results_destination_port:
        for record in table.records:
            port = record.values.get('destination_ports')
            if port is not None and len(port) == 5 and port.isalpha():
                port_set.add(port)
    results_port = query_api.query(query_port)
    for table in results_port:
        for record in table.records:
            port = record.values.get('port')
            if port is not None and len(port) == 5 and port.isalpha():
                port_set.add(port)
    return port_set  # {'KRINC', 'THKSI', 'JPCHB', '....}
    # print(len(port_set)) #839


def crawl_cordinate(portname):
    data ={}
    with webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options) as driver:
        try:
            driver.get(f'https://www.vesselfinder.com/ports/{portname}001')
            try:
                location = driver.find_element(By.CLASS_NAME, "text1").text

                parts = location.split(" is located in ")
                city = parts[0].replace("Port of ", "").strip()
                rest = parts[1].split(" at ")
                country = rest[0].strip()
                coords = rest[1].split(', ')
                latitude = coords[0].strip()
                longitude = coords[1].split('.\n')[0].strip()

                data = {
                    "portname": portname,
                    "city": city,
                    "country": country,
                    "latitude": latitude,
                    "longitude": longitude,
                    "timestamp": datetime.datetime.now(pytz.timezone('Asia/Taipei')).isoformat()
                }
                logging.info(f"Data successfully collected for {portname}")
            except NoSuchElementException:
                logging.error(f"No data found for {portname}. Skipping this port.")
        except Exception as e:
            logging.error(f"Error accessing for {portname}: {e}")

    return data

def upload_to_influxdb():
    with open('data/port_data.json', 'r') as f:
        ports_data = json.load(f)

        for data in ports_data:
            try:
                latitude_number, latitude_directtion = float(data['latitude'][:-1]), data['latitude'][-1]
                if latitude_directtion == 'S':
                    latitude_number *= -1
                longitude_number, longitude_direction = float(data['longitude'][:-1]), data['longitude'][-1]
                if longitude_direction == "W":
                    longitude_direction *=-1
                print(latitude_number,longitude_number)

                point = Point("port_data") \
                    .tag("portname", data['portname']) \
                    .tag("city", data['city']) \
                    .tag("country", data['country']) \
                    .field("latitude", latitude_number) \
                    .field("longitude", longitude_number) \
                    .time(data['timestamp'])

                write_api.write(bucket=bucket, org=org, record=point)
                logging.info(f"Data successfully written to InfluxDB for {data['portname']}")

            except Exception as e:
                logging.error(f"Error writing to InfluxDB for {data['portname']}: {e}")
                client = InfluxDBClient(token=token, url=url, org=org, timeout=90000)
                write_api = client.write_api(write_options=SYNCHRONOUS, timeout=900000)



all_ports =[]
ports = get_port()
print(len(ports))
for port in ports:
    port_data=crawl_cordinate(port)
    if port_data:
        all_ports.append(port_data)
print(all_ports)
with open('data/port_data.json', 'w') as f:
    json.dump(all_ports, f)

upload_to_influxdb()

