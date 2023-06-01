#!/usr/bin/env python3

import logging
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from slot_finder import SlotFinder
from slot_reservation import SlotReservation

TARGET_RUN_TIME = "18:00:00"


class SlotBookingApp:
    """
    Class representing a slot booking application.
    """

    def __init__(self):
        """
        Initialize the SlotBookingApp instance.
        """
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.schedule_json_path = os.path.join(
            self.script_dir, '..', 'schedule.json'
        )

    def run(self):
        """
        Run the slot booking application.
        """
        logging.basicConfig(level=logging.INFO)
        logging.getLogger('WDM').setLevel(logging.ERROR)

        try:
            finder = SlotFinder(self.schedule_json_path)
            available_slots = finder.find_slots()

            if TARGET_RUN_TIME == "18:00:00":
                current_time = time.strftime("%H:%M:%S")
                while current_time < TARGET_RUN_TIME:
                    time.sleep(1)
                    current_time = time.strftime("%H:%M:%S")
                    message = (
                        f'Waiting for {TARGET_RUN_TIME} to '
                        f'start booking, current time {current_time}...'
                    )
                    logging.info(message)

            chrome_options = Options()
            chrome_options.add_argument("--headless")
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)

            reservation = SlotReservation()

            for recreation_name, recreation_details in available_slots.items():
                for recreation_slot in recreation_details["slots"]:
                    reservation.reserve_slots(driver,
                                              recreation_name,
                                              recreation_details,
                                              recreation_slot)

        except Exception as err:
            logging.error('❌ Exception: %s', err)


def main():
    """
    Entry point for the application script.
    """
    slot_booking_app = SlotBookingApp()
    slot_booking_app.run()


if __name__ == "__main__":
    main()
