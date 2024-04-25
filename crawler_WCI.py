# from selenium import webdriver
from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import requests
import gzip
import brotli
import time
import json

import io
options = Options()
options.add_argument('--headless')  # run in headless mode.
options.add_argument('--disable-gpu')  # disable GPU hardware acceleration.
options.add_argument('start-maximized')  # open the window at max size for the screen.
options.add_argument('disable-infobars')  # prevent Chrome from displaying
options.add_argument('--disable-extensions')  # disable all browser extensions.

def crawler():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get("https://www.macromicro.me/toolbox/chart-builder/line?chart=44756")

    # Wait for the JavaScript to execute (adjust the sleep time as needed)
    time.sleep(5)

    # Find the element containing the JSON data (you might need to adjust the selector)
    json_element = driver.find_element(By.TAG_NAME, 'pre')

    # Extract the JSON data
    json_data = json.loads(json_element.text)

    # Print or process the JSON data
    print(json_data)

    # Clean up
    driver.quit()
#     driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), seleniumwire_options=options)
#
#
#     url = "https://www.macromicro.me/toolbox/chart-builder/get-series"
#     driver.get(url)
#     driver.wait_for_request('/get-series', timeout=30)
#
#     for request in driver.requests:
#         if request.response and 'get-series' in request.path:
#             body = request.response.body
#             print(body)
#             # print('request.response.headers', request.response.headers)
#             if request.response.headers.get('Content-Encoding') == 'br':
#                 print(1)
#                 decompressed_body = brotli.decompress(body)
#
#                 data = json.loads(decompressed_body.decode('utf-8'))
#                 print(data)
#
#     driver.quit()
#
crawler()



# Add the necessary headers from your request
# headers = {
#     'Accept': '*/*',
#     'Accept-Encoding': 'gzip, deflate, br',
#     'Accept-Language': 'en-US,en;q=0.9',
#     'Authorization': 'Bearer 6082d8b20ec7b3763816acd66fee108c',  # Your API key here
#     'Content-Type': 'text/plain;charset=UTF-8',
# }
#
# # The body of your POST request. You will need to replicate this from your browser's request payload.
# data = {
#     "date": "value1",
#     "value": "value2",
# }
#
# # Make the POST request
# response = requests.post('https://www.macromicro.me/toolbox/chart-builder/get-series', headers=headers, json=data)
#
# # If the response was sent with Brotli encoding, decompress it
# if response.headers.get('Content-Encoding') == 'br':
#     print(response.content[:100])
#     decompressed_data = brotli.decompress(response.content)
#     data = json.loads(decompressed_data.decode('utf-8'))
# else:
#     data = response.json()
#
# # Now `data` is a Python dictionary containing the response data
# print(data)
