import logging
import time
from email_confirmation import ConfirmationCodeExtractor
from selenium.webdriver.common.by import By
from telegram_bot import TelegramBot
from env_vars import EnvVars
import config

# Initialize environment variables and Telegram bot
env_vars = EnvVars.check_env_vars(EnvVars.REQUIRED_VARS)
env_var = EnvVars(env_vars)
telegram_bot = TelegramBot(env_var)


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
        reservation_count_input.send_keys(config.GROUP_SIZE)
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
