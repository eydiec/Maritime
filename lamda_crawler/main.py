from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from dotenv import load_dotenv
import datetime
import logging
import pytz
import os

options = Options()
service = webdriver.ChromeService("/opt/chromedriver") #for docker
options.binary_location = '/opt/chrome/chrome'
options.add_argument("--headless")
options.add_argument('--no-sandbox')
options.add_argument("--disable-gpu")
options.add_argument("--single-process")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-dev-tools")
options.add_argument("--no-zygote")
options.add_argument("--remote-debugging-port=9222")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def handler(): #for daily congestion

    load_dotenv()
    influx_url = os.getenv('INFLUX_URL')
    org = os.getenv('INFLUX_ORG')
    token = os.getenv('INFLUX_TOKEN')
    bucket = os.getenv('INFLUX_BUCKET')
    with InfluxDBClient(token=token, url=influx_url, org=org) as client, \
            webdriver.Chrome(options=options, service=service) as driver: #for docker
# driver = webdriver.Chrome(options=options, service=service)
        url = 'https://www.gocomet.com/real-time-port-congestion/taiwan'
        driver.get(url)
        items = driver.find_elements(By.CSS_SELECTOR, "ul .list-item .item-info")
        write_api = client.write_api(write_options=SYNCHRONOUS, timeout=900000)

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


        ports=['TWKHH', 'TWKEL','TWTXG','TWTPE']
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






