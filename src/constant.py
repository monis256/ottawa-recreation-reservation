# Email Configuration
FROM_EMAIL = "noreply@frontdesksuite.com"
"""
The email address from which the email is received.
"""

FROM_SUBJECT = "Verify your email"
"""
The subject of the email.
"""

# Application Configuration
CRON_MODE = True
"""
Set to True for automatic scheduled runs using cron.
Set to False for manual runs.
"""

GROUP_SIZE = 1
"""
The number of people in your group.
"""

TG_API_URL = "https://api.telegram.org/bot"
"""
The URL of the Telegram API.
"""

CHROME_HEADLESS = True
"""
Set to True for running Chrome in headless mode (without a visible window).
Set to False for watching the Chrome window during execution.
"""

MAX_RETRIES = 3
"""
The number of retries for clicking the Confirm button.
"""

SCHEDULE_JSON = "schedule.json"
"""
The name of the JSON file containing the schedule.
"""

# Reservation Configuration
TARGET_RUN_TIME = "18:00:00"
"""
The time when the reservation begins.
"""

PRIOR_DAYS = 2
"""
The number of days in advance to enable reservations.
"""
