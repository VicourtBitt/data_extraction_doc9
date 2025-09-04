from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import time

from pathlib import Path
import os

import logging 

from utils import filter_all_invoices_by_date, generate_csv, download_invoices, time_execution_counter

# Logging Configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# Constants
BASE_URL = os.getenv("BASE_URL", "https://rpachallengeocr.azurewebsites.net/")
DOWNLOAD_FOLDER = Path(os.getenv("DOWNLOAD_FOLDER", "invoices"))
CSV_NAME = os.getenv("CSV_NAME", "filtered_invoices.csv")
TIMEOUT = int(os.getenv("TIMEOUT", 10))


# The kind of docstring used here is a Sphinx-like style, it's quite verbose
# but I find it more readable and easier to setup than just a simple one-liner phrase

def get_chrome_web_driver(headless: bool = True):
    """
    Automatically searches or install the Chrome WebDriver

    Parameters
    ----------
    headless : bool
        Whether to run the browser in headless mode or not.
    """
    try:
        # Initialize the Chrome options to setup the headless mode
        options = Options()
        if headless:
            options.add_argument("--headless=new")
            logger.info("Running Chrome in headless mode")

        # Initialize the Driver and then return it
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        logger.info("Chrome WebDriver has been initialized")
        return driver
    except Exception as e:
        logger.error(f"Error occurred while setting up Chrome WebDriver: {e}")


def extract_data_with_pagination(driver: WebDriver):
    """
    Extract data from the table, going through each pagination step

    Parameters
    ----------
    driver : WebDriver
        The Chrome WebDriver instance
    """
    driver.get(BASE_URL)
    invoices = []
    wait = WebDriverWait(driver, TIMEOUT)
    # I've had a problem with a racing condition previously, so this was the only
    # possible way I found to fix, constantly verifying the current page number
    current_page = 1

    while True:
        try:
            logger.info(f"Scraping page {current_page}...")
            
            wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#tableSandbox > tbody > tr")))
            tbody = driver.find_element(By.CSS_SELECTOR, "#tableSandbox > tbody")
            rows = tbody.find_elements(By.TAG_NAME, "tr")

            for row in rows:
                cols = row.find_elements(By.TAG_NAME, "td")
                if len(cols) == 4:
                    invoices.append({
                        "ID": cols[1].text,
                        "DueDate": cols[2].text,
                        "URL": cols[3].find_element(By.TAG_NAME, "a").get_attribute("href")
                    })

            next_button = driver.find_element(By.ID, "tableSandbox_next")
            if "disabled" in next_button.get_attribute("class"):
                logger.info("Last page reached. All data extracted.")
                break

            logger.info("Navigating to the next page...")
            # The next_button.click() worked, but as I saw, entering the element and
            # using JavaScript to click it was more reliable/robust
            driver.execute_script("arguments[0].click();", next_button)
            
            current_page += 1
            # I was using a CSS_SELECTOR / ID tracker, but my last attempt failed
            # so I'll be using a XPath locator to track the next step
            next_page_locator = (By.XPATH, f"//a[contains(@class, 'paginate_button') and contains(@class, 'current') and text()='{current_page}']")
            
            wait.until(EC.visibility_of_element_located(next_page_locator))

        except (TimeoutException, NoSuchElementException) as e:
            logger.error(f"An error occurred: {e}")
            break

    return invoices


@time_execution_counter
def main():
    driver = get_chrome_web_driver(headless=True)
    if not driver:
        logger.error("Failed to initialize web driver.")
        return

    try:
        start = time.time()
        invoices = extract_data_with_pagination(driver)
        filtered_invoices = filter_all_invoices_by_date(invoices)
        generate_csv(filtered_invoices, CSV_NAME)
        end = time.time()
        logger.info(f"Data extraction and processing completed in {end - start:.2f} seconds.")
        download_invoices(filtered_invoices, DOWNLOAD_FOLDER)

    except Exception as e:
        logger.error(f"Error occurred in main: {e}")

    finally:
        if driver:
            driver.quit()
            logger.info("Chrome WebDriver has been closed")


if __name__ == "__main__":
    main()