import datetime
import json
import sys
import logging
from typing import Dict, Any, List


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
        with open(self.json_file_path) as file:
            data: Dict[str, Any] = json.load(file)

        logging.info('Looking for available slots...')
        curr_date: datetime.date = datetime.date.today()
        future_weekday: datetime.date = curr_date + datetime.timedelta(days=2)
        future_weekday_iso: int = future_weekday.isoweekday()

        # Find facilities with available slots
        available_facilities: Dict[str, Dict[str, Any]] = {}
        for facility in data["facilities"]:
            facility_name: str = facility["name"]
            facility_schedule: List[Dict[str, Any]] = facility["schedule"]
            facility_link: str = facility["link"]
            facility_activity_button: str = facility["activity_button"]
            slots: List[Dict[str, Any]] = []

            for slot in facility_schedule:
                slot_day_of_week: int = slot["day_of_week"]
                slot_starting_time: str = slot["starting_time"]
                slot_follow: bool = slot["follow"]

                if future_weekday_iso == slot_day_of_week and slot_follow:
                    message: str = (
                        f'✅ Slot found in {facility_name} '
                        f'on {future_weekday} at {slot_starting_time}'
                    )
                    logging.info(message)

                    slot_data: Dict[str, Any] = {
                        "day_of_week": slot_day_of_week,
                        "starting_time": slot_starting_time
                    }
                    slots.append(slot_data)

                    facility_data: Dict[str, Any] = {
                        "link": facility_link,
                        "activity_button": facility_activity_button,
                        "slots": slots
                    }

                    available_facilities[facility_name] = facility_data

        if not available_facilities:
            logging.error('❌ No slots found for %s', future_weekday)
            sys.exit()

        return available_facilities
