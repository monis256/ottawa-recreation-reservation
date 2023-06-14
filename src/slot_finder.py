import datetime
import json
import sys
import logging
from typing import Dict, Any, List
from constant import PRIOR_DAYS


class SlotFinder:
    """
    A class for finding available slots.

    Methods:
    - __init__(json_file_path: str):
        Initialize the SlotFinder class.
    - find_slots() -> Dict[str, Dict[str, Any]]:
        Find available slots based on the provided JSON file.
    """

    def __init__(self, json_file_path: str) -> None:
        """
        Initialize the SlotFinder class.

        Args:
            json_file_path (str): Path to the JSON file containing slot data.
        """
        self.json_file_path: str = json_file_path

    def find_slots(self) -> Dict[str, Dict[str, Any]]:
        """
        Find available slots based on the provided JSON file.

        Returns:
            dict: Dictionary containing available slots grouped by facility.
        """
        with open(self.json_file_path, encoding="utf-8") as file:
            try:
                data: Dict[str, Any] = json.load(file)
            except json.JSONDecodeError as err:
                logging.error('❌ Error decoding JSON: %s', err)
                sys.exit(1)

        logging.info('Looking for available slots...')
        future_weekday: datetime.date = (
            datetime.date.today() + datetime.timedelta(days=PRIOR_DAYS)
        )
        future_weekday_iso: int = future_weekday.isoweekday()

        # Find facilities with available slots
        available_facilities: Dict[str, Dict[str, Any]] = {}
        for facility in data["facilities"]:
            slots: List[Dict[str, Any]] = []

            for slot in facility["schedule"]:
                if (
                    future_weekday_iso == slot["day_of_week"] and
                    slot["follow"]
                ):
                    message: str = (
                        f'✅ Slot found in {facility["name"]} '
                        f'on {future_weekday} at {slot["starting_time"]}'
                    )
                    logging.info(message)

                    slot_data: Dict[str, Any] = {
                        "day_of_week": slot["day_of_week"],
                        "starting_time": slot["starting_time"]
                    }
                    slots.append(slot_data)

                    facility_data: Dict[str, Any] = {
                        "link": facility["link"],
                        "activity_button": facility["activity_button"],
                        "slots": slots
                    }

                    available_facilities[facility["name"]] = facility_data

        if not available_facilities:
            logging.error('❌ No slots found for %s', future_weekday)
            sys.exit(0)

        return available_facilities
