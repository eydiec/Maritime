from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from dotenv import load_dotenv
import datetime
import logging
import pytz
import os

options = Options()
# options.add_argument('--headless')  # run in headless mode.
options.add_argument('--disable-gpu')  # disable GPU hardware acceleration.
options.add_argument('start-maximized')  # open the window at max size for the screen.
options.add_argument('disable-infobars')  # prevent Chrome from displaying
options.add_argument('--disable-extensions')  # disable all browser extensions.

load_dotenv()
url = os.getenv('INFLUX_URL')
org = os.getenv('INFLUX_ORG')
token = os.getenv('INFLUX_TOKEN')
bucket = os.getenv('INFLUX_BUCKET')

# Connect to InfluxDB
try:
    client = InfluxDBClient(token=token, url=url, org=org)
    # InfluxDB
    write_api = client.write_api(write_options=SYNCHRONOUS, timeout=900000)
    query_api = client.query_api()
    logging.info("successfully connect to InfluxDB")
except Exception as e:
    logging.error('fail to connect with InfluxDB')

def crawler(): #for daily congestion
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    url = 'https://www.gocomet.com/real-time-port-congestion/taiwan'
    driver.get(url)
    items = driver.find_elements(By.CSS_SELECTOR, "ul .list-item .item-info")

    for item in items:
        port_name_element = item.find_element(By.CSS_SELECTOR, ".flag-and-name .name")
        delay_element = item.find_element(By.CSS_SELECTOR, ".list-item-right .delay")

        port_name = port_name_element.text.split(",")[-1].strip()
        delay = delay_element.text.split(" ")[0]

        if port_name and delay:
            print(f"{port_name}: {delay} day(s)")
            point = Point("port_congestion").tag("port_name", port_name).field("delay", int(delay)).time(datetime.datetime.now(pytz.timezone('Asia/Taipei')))
            # print(point)
            write_api.write(bucket=bucket, org=org, record=point)

    driver.quit()
    write_api.close()

def cralwer_24hr(): #for vessels have arrived within the past 24 hours
    ports=['TWKHH', 'TWKEL','TWTXG','TWTPE']
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    for port in ports:

        url = f'https://www.vesselfinder.com/ports/{port}001'
        driver.get(url)
        location = driver.find_element(By.CLASS_NAME, "text1").text
        arrived_vessel = location.split('.\n')[1].split(' ')[0].strip()
        vessel_in_port = driver.find_element(By.XPATH, "//div[@class='pei']/div[span[text()='Ships in port:']]/strong").text

        point = Point("port_congestion").tag("port_name", port).field("vessel_in_24hr", int(arrived_vessel)).field("vessel_in_port", int(vessel_in_port)).time(
            datetime.datetime.now(pytz.timezone('Asia/Taipei')))

        write_api.write(bucket=bucket, org=org, record=point)

        print(port, arrived_vessel,vessel_in_port)
    driver.quit()
    write_api.close()





crawler()
cralwer_24hr()