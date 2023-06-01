import datetime
import json
import sys
import logging


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
