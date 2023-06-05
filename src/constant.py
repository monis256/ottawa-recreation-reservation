FROM_EMAIL = "noreply@frontdesksuite.com"  # The email get receive from
FROM_SUBJECT = "Verify your email"  # The subject of email
CRON_MODE = True  # Set to False in case of manual run
GROUP_SIZE = 1   # How many people in your group?
TG_API_URL = "https://api.telegram.org/bot"  # Telegram API URL
CHROME_HEADLESS = True  # Set to False for watching Chrome window
MAX_RETRIES = 10  # Retries count for Confirm button
SCHEDULE_JSON = "schedule.json"  # Name of json file with the schedule
TARGET_RUN_TIME = "18:00:00"  # Time when the reservation begins
