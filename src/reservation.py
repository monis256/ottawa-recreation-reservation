#!/usr/bin/env python3

import datetime
import json
import logging
import os
import sys
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from env_vars import EnvVars
from email_confirmation import ConfirmationCodeExtractor
from telegram_bot import TelegramBot

# Initialize environment variables and Telegram bot
env_vars = EnvVars.check_env_vars(EnvVars.REQUIRED_VARS)
env_var = EnvVars(env_vars)
telegram_bot = TelegramBot(env_var)

script_dir = os.path.dirname(os.path.abspath(__file__))
schedule_json_path = os.path.join(script_dir, '..', 'schedule.json')

GROUP_SIZE = 1
#TARGET_RUN_TIME = "18:00:00"


def find_slots(json_file_path):
    with open(json_file_path) as file:
        data = json.load(file)

    logging.info('Looking for available slots...')
    current_date = datetime.date.today()
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
            slot_follow = slot["follow"]

            if future_weekday_iso == slot_day_of_week and slot_follow:
                message = f'✅ Slot found in {facility_name} on {future_weekday} at {slot_starting_time}'
                logging.info(message)

                slot_data = {
                    "day_of_week": slot_day_of_week,
                    "starting_time": slot_starting_time
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
        message = f'Booking slot in {recreation_name} at {recreation_slot["starting_time"]}...'
        logging.info(message)

        driver.get(recreation_details["link"])
        driver.find_element(By.XPATH, "//div[text()='" + recreation_details["activity_button"] + "']").click()

        reservation_count_input = driver.find_element(By.ID, "reservationCount")
        # When page doesn't have dialogue 'How many people in your group?'
        if reservation_count_input.get_attribute("type") == "hidden":
            message = f'❌ No slots available in {recreation_name} at {recreation_slot["starting_time"]} ({recreation_details["activity_button"]})'
            logging.error(message)
            telegram_bot.send_message(message)
            telegram_bot.send_photo(driver.get_screenshot_as_png())
            return False

        reservation_count_input.clear()
        reservation_count_input.send_keys(GROUP_SIZE)
        driver.find_element(By.CLASS_NAME, "mdc-button__ripple").click()
        driver.find_element(By.CLASS_NAME, "date-text").click()
        driver.find_element(By.XPATH, "//a[contains(span[@class='mdc-button__label available-time'], '" + recreation_slot["starting_time"] + "')]").click()

        telephone_input = driver.find_element(By.ID, "telephone")
        telephone_input.clear()
        telephone_input.send_keys(env_var.phone_number)

        email_input = driver.find_element(By.ID, "email")
        email_input.clear()
        email_input.send_keys(env_var.imap_email)

        name_input = driver.find_element(By.ID, "field2021")
        name_input.clear()
        name_input.send_keys(env_var.name)
        time.sleep(1)

        driver.find_element(By.CLASS_NAME, "mdc-button__ripple").click()

        confirmation_code = None
        while confirmation_code is None:
            time.sleep(1)
            logging.info("Waiting for a code to verify booking...")
            extractor = ConfirmationCodeExtractor(env_var.imap_server, env_var.imap_email, env_var.imap_password)
            confirmation_code = extractor.get_confirmation_code()

        logging.info('✅ Verification code is %s', confirmation_code)

        code_input = driver.find_element(By.ID, "code")
        code_input.clear()
        code_input.send_keys(confirmation_code)
        driver.find_element(By.CLASS_NAME, "mdc-button__ripple").click()

        message = f'✅ Successfully booked a slot in {recreation_name} at {recreation_slot["starting_time"]} ({recreation_details["activity_button"]})'
        logging.info(message)
        telegram_bot.send_message(message)
        telegram_bot.send_photo(driver.get_screenshot_as_png())

    except Exception as err:
        message = f'❌ Failed to book a slot in {recreation_name} at {recreation_slot["starting_time"]} ({recreation_details["activity_button"]}), exception: {err}'
        logging.error(message)
        telegram_bot.send_message(message)
        telegram_bot.send_photo(driver.get_screenshot_as_png())


def main():

    # """Entry point for the application script"""
    logging.basicConfig(level=logging.INFO)
    logging.getLogger('WDM').setLevel(logging.ERROR)

    try:
        available_slots = find_slots(schedule_json_path)

        if TARGET_RUN_TIME:
            current_time = time.strftime("%H:%M:%S")
            while current_time < TARGET_RUN_TIME:
                time.sleep(1)
                current_time = time.strftime("%H:%M:%S")
                logging.info("Waiting for a %s to start booking, current time %s...", TARGET_RUN_TIME, current_time)

        chrome_options = Options()
        # chrome_options.add_argument("--headless")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)

        for recreation_name, recreation_details in available_slots.items():
            for recreation_slot in recreation_details["slots"]:
                reserve_slots(driver, recreation_name, recreation_details, recreation_slot)

    except Exception as err:
        logging.error('❌ Exception: %s', err)


if __name__ == "__main__":
    main()
