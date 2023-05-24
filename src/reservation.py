#!/usr/bin/env python3

import datetime
import json
import logging
import sys
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
#from selenium.webdriver.support.select import Select
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
# from env_vars import EnvVars
# from telegram_bot import TelegramBot

#SCHEDULE_JSON_PATH = '../json/schedule.json'
RESERVE_JSON_PATH = '../json/reserve.json'


def find_slots(json_file_path):
    with open(json_file_path) as file:
        data = json.load(file)

    logging.info('Looking for available slots...')
    current_date = datetime.date.today() # + datetime.timedelta(days=1)
    future_weekday = current_date + datetime.timedelta(days=2)
    future_weekday_iso = future_weekday.isoweekday()

    # Find facilities with available slots
    available_facilities = {}
    for facility in data["facilities"]:
        facility_name = facility["name"]
        facility_schedule = facility["schedule"]
        facility_link = facility["link"]
        facility_activity_button = facility["activity_button"]
        slots = []

        for slot in facility_schedule:
            slot_day_of_week = slot["day_of_week"]
            slot_starting_time = slot["starting_time"]
            slot_ending_time = slot["ending_time"]

            if future_weekday_iso == slot_day_of_week:
                message = f'✅ Slot found in {facility_name} on {future_weekday} at {slot_starting_time} - {slot_ending_time}'
                logging.info(message)

                slot_data = {
                    "day_of_week": slot_day_of_week,
                    "starting_time": slot_starting_time,
                    "ending_time": slot_ending_time
                }
                slots.append(slot_data)

                facility_data = {
                    "link": facility_link,
                    "activity_button": facility_activity_button,
                    "slots": slots
                }

                available_facilities[facility_name] = facility_data

    if not available_facilities:
        logging.error('❌ No slots found for %s', future_weekday)
        sys.exit()

    return available_facilities

def reserve_slots(driver, recreation_name, recreation_details, recreation_slot):
    try:
        message = f'Booking slot in {recreation_name} at {recreation_slot["starting_time"]} - {recreation_slot["ending_time"]}...'
        logging.info(message)

        driver.get(recreation_details["link"])
        driver.find_element(By.XPATH, "//div[text()='" + recreation_details["activity_button"] + "']").click()

        time.sleep(2) # TEMP TOREMOVE

    except Exception as err:
        logging.error('❌ Exception: %s', err)

def main():

    # """Entry point for the application script"""
    logging.basicConfig(level=logging.INFO)
    logging.getLogger('WDM').setLevel(logging.ERROR)

    try:
        available_slots = find_slots(RESERVE_JSON_PATH)

        print("")

        chrome_options = Options()
        #chrome_options.add_argument("--headless")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)

        for recreation_name, recreation_details in available_slots.items():
            for recreation_slot in recreation_details["slots"]:
                reserve_slots(driver, recreation_name, recreation_details, recreation_slot)

    except Exception as err:
        logging.error('❌ Exception: %s', err)


if __name__ == "__main__":
    main()
