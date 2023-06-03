#!/usr/bin/env python3

import logging
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from typing import Dict, Any
from webdriver_manager.chrome import ChromeDriverManager
from slot_finder import SlotFinder
from slot_reservation import SlotReservation

TARGET_RUN_TIME = "18:00:00"  # Time when the registration begins
SCHEDULE_JSON = "schedule.json"  # Name of json file with the schedule
CRON_MODE = True  # Set to False in case of manual run


class SlotRegistrationApp:
    """
    Class representing a slot registration application.

    Methods:
    - __init__():
        Initialize the SlotRegistrationApp instance.
    - run():
        Run the slot registration application.
    """
    def __init__(self) -> None:
        """
        Initialize the SlotRegistrationApp instance.
        """
        self.script_dir: str = os.path.dirname(os.path.abspath(__file__))
        self.schedule_json_path: str = os.path.join(
            self.script_dir, '..', SCHEDULE_JSON
        )

    def run(self) -> None:
        """
        Run the slot registration application.
        """
        logging.basicConfig(level=logging.INFO)
        logging.getLogger('WDM').setLevel(logging.ERROR)

        try:
            finder: SlotFinder = SlotFinder(self.schedule_json_path)
            available_slots: Dict[str, Dict[str, Any]] = finder.find_slots()

            if CRON_MODE:
                current_time: str = time.strftime("%H:%M:%S")
                while current_time < TARGET_RUN_TIME:
                    time.sleep(3)
                    current_time = time.strftime("%H:%M:%S")
                    message: str = (
                        f'Waiting for {TARGET_RUN_TIME} to '
                        f'start registration, current time {current_time}...'
                    )
                    logging.info(message)

            chrome_options: Options = Options()
            chrome_options.add_argument("--headless")
            service: Service = Service(ChromeDriverManager().install())
            driver: webdriver.Chrome = webdriver.Chrome(service=service,
                                                        options=chrome_options)

            reservation: SlotReservation = SlotReservation()

            for rec_name, rec_details in available_slots.items():
                for rec_slot in rec_details["slots"]:
                    reservation.reserve_slots(driver, rec_name,
                                              rec_details, rec_slot)

        except Exception as err:
            logging.error('❌ Exception: %s', err)


def main() -> None:
    """
    Entry point for the application script.
    """
    slot_registration_app: SlotRegistrationApp = SlotRegistrationApp()
    slot_registration_app.run()


if __name__ == "__main__":
    main()
