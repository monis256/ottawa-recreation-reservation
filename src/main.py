#!/usr/bin/env python3

import logging
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from find_slots import find_slots
from reserve_slots import reserve_slots
import config

script_dir = os.path.dirname(os.path.abspath(__file__))
schedule_json_path = os.path.join(script_dir, '..', 'schedule.json')


def main():
    # """Entry point for the application script"""
    logging.basicConfig(level=logging.INFO)
    logging.getLogger('WDM').setLevel(logging.ERROR)

    try:
        available_slots = find_slots(schedule_json_path)

        if config.TARGET_RUN_TIME == "18:00:00":
            current_time = time.strftime("%H:%M:%S")
            while current_time < config.TARGET_RUN_TIME:
                time.sleep(1)
                current_time = time.strftime("%H:%M:%S")
                logging.info("Waiting for a %s to start booking, current time %s...", config.TARGET_RUN_TIME, current_time)

        chrome_options = Options()
        chrome_options.add_argument("--headless")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)

        for recreation_name, recreation_details in available_slots.items():
            for recreation_slot in recreation_details["slots"]:
                reserve_slots(driver, recreation_name, recreation_details, recreation_slot)

    except Exception as err:
        logging.error('❌ Exception: %s', err)


if __name__ == "__main__":
    main()
