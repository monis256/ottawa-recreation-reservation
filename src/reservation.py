#!/usr/bin/env python3

import datetime
import json
import logging
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
#from selenium.webdriver.common.by import By
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

    current_date = datetime.date.today() + datetime.timedelta(days=1)
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
                    "name": facility_name,
                    "link": facility_link,
                    "activity_button": facility_activity_button,
                    "slots": slots
                }
                available_facilities[facility_name] = facility_data
                available_slots = json.dumps(available_facilities, indent=2)

    if not available_facilities:
        logging.error('❌ No slots found for %s', future_weekday)
        sys.exit()

    return available_slots

def reserve_slots(driver):
    print("test")

def main():

    # """Entry point for the application script"""
    logging.basicConfig(level=logging.INFO)
    logging.getLogger('WDM').setLevel(logging.ERROR)

    try:
        available_slots = find_slots(RESERVE_JSON_PATH)
        print(available_slots)

        #chrome_options = Options()
        #chrome_options.add_argument("--headless")

        #service = Service(ChromeDriverManager().install())
        #driver = webdriver.Chrome(service=service, options=chrome_options)
        # TODO: parse json, for every slot run reserve_slots function
        # and book slot (gmail integration + tg integration)

    except Exception as err:
        logging.error('❌ Exception: %s', err)


if __name__ == "__main__":
    main()
