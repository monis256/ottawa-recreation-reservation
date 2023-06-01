import logging
import time
from selenium.webdriver.common.by import By
from confirmation_code_extractor import ConfirmationCodeExtractor
from telegram_bot import TelegramBot
from env_vars import EnvVars

GROUP_SIZE = 1


class SlotReservation:
    def __init__(self):
        """
        Initializes SlotReservation class.

        Initializes environment variables and Telegram bot.
        """
        env_vars = EnvVars.check_env_vars(EnvVars.REQUIRED_VARS)
        self.env_var = EnvVars(env_vars)
        self.telegram_bot = TelegramBot(self.env_var)

    def reserve_slots(self, driver, recreation_name,
                      recreation_details, recreation_slot):
        """
        Reserves slots in the given recreation facility.

        Args:
            driver: WebDriver object for interacting with the web browser.
            recreation_name (str): Name of the recreation facility.
            recreation_details (dict): Details of the recreation facility.
            recreation_slot (dict): Details of the slot to be reserved.
        """
        try:
            message = (
                f'Booking slot in {recreation_name} at '
                f'{recreation_slot["starting_time"]}...'
            )
            logging.info(message)

            driver.get(recreation_details["link"])
            driver.find_element(
                By.XPATH,
                "//div[text()='" + recreation_details["activity_button"] + "']"
            ).click()

            reservation_count_input = driver.find_element(
                By.ID, "reservationCount"
            )
            # When page doesn't have dialogue 'How many people in your group?'
            if reservation_count_input.get_attribute("type") == "hidden":
                message = (
                    f'❌ No slots available in {recreation_name} at '
                    f'{recreation_slot["starting_time"]} '
                    f'({recreation_details["activity_button"]})'
                )
                logging.error(message)
                self.telegram_bot.send_message(message)
                self.telegram_bot.send_photo(driver.get_screenshot_as_png())
                return False

            reservation_count_input.clear()
            reservation_count_input.send_keys(GROUP_SIZE)
            driver.find_element(By.CLASS_NAME, "mdc-button__ripple").click()
            driver.find_element(By.CLASS_NAME, "date-text").click()
            class_name = "mdc-button__label available-time"
            driver.find_element(
                By.XPATH,
                "//a[contains(span[@class='" + class_name + "'], '" +
                recreation_slot["starting_time"] + "')]"
            ).click()

            telephone_input = driver.find_element(By.ID, "telephone")
            telephone_input.clear()
            telephone_input.send_keys(self.env_var.phone_number)

            email_input = driver.find_element(By.ID, "email")
            email_input.clear()
            email_input.send_keys(self.env_var.imap_email)

            name_input = driver.find_element(By.ID, "field2021")
            name_input.clear()
            name_input.send_keys(self.env_var.name)
            time.sleep(1)

            driver.find_element(By.CLASS_NAME, "mdc-button__ripple").click()
            # TODO: handle retry text and press retry button

            confirmation_code = None
            while confirmation_code is None:
                time.sleep(1)
                logging.info("Waiting for a code to verify booking...")
                extractor = ConfirmationCodeExtractor(
                    self.env_var.imap_server,
                    self.env_var.imap_email,
                    self.env_var.imap_password
                )
                confirmation_code = extractor.get_confirmation_code()

            logging.info('✅ Verification code is %s', confirmation_code)

            code_input = driver.find_element(By.ID, "code")
            code_input.clear()
            code_input.send_keys(confirmation_code)
            driver.find_element(By.CLASS_NAME, "mdc-button__ripple").click()

            message = (
                f'✅ Successfully booked a slot in {recreation_name} '
                f'at {recreation_slot["starting_time"]} '
                f'({recreation_details["activity_button"]})'
            )
            logging.info(message)
            self.telegram_bot.send_message(message)
            self.telegram_bot.send_photo(driver.get_screenshot_as_png())

        except Exception as err:
            message = (
                f'❌ Failed to book a slot in {recreation_name} '
                f'at {recreation_slot["starting_time"]} '
                f'({recreation_details["activity_button"]}), exception: {err}'
            )
            logging.error(message)
            self.telegram_bot.send_message(message)
            self.telegram_bot.send_photo(driver.get_screenshot_as_png())
