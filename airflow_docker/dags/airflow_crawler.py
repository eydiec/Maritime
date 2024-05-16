import datetime

from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium import webdriver
import logging
import pytz
import time

logging.basicConfig(level=logging.INFO)

options = Options()
options.add_argument('--headless')  # run in headless mode.
options.add_argument('--disable-gpu')  # disable GPU hardware acceleration.
options.add_argument('start-maximized')  # open the window at max size for the screen.
options.add_argument('disable-infobars')  # prevent Chrome from displaying
options.add_argument('--disable-extensions')  # disable all browser extensions.

def web_crawler():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    url = 'https://www.gocomet.com/real-time-port-congestion'
    driver.get(url)

    search_bar = driver.find_element(By.XPATH, "//input[@class='ant-input'][@placeholder='Search for country or port']")
    search_bar.clear()  # Clear any pre-existing text
    search_bar.send_keys('Taiwan')

    time.sleep(5)

    date = datetime.datetime.now(pytz.timezone('Asia/Taipei'))
    containers = driver.find_elements(By.XPATH, "//div[contains(@class, 'list-item')]")


    for container in containers:
        port = container.find_element(By.XPATH, ".//div[contains(@class, 'name')]").text
        delay_day = container.find_element(By.XPATH, ".//div[contains(@class, 'delay')]").text

        print(port, delay_day,date)
        # logging.info(
        #     f"{port}, Date: {date.strftime('%Y-%m-%d %H:%M:%S')}, Delay: {delay_day[0].text.split()[0]} days")

    driver.quit()


web_crawler()