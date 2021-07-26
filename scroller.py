import time
import conf as CFG
from selenium import webdriver

class Scroller:
    """Class responsible to scroll web sites and take the page source of them."""

    def __init__(self, site_url, logger):
        self._base_url = site_url
        self._driver = webdriver.Chrome(CFG.CHROME_DRIVER_PATH) if CFG.CHROME_DRIVER_PATH else webdriver.Chrome()
        self._logger = logger
        self._page_source = None

    def __enter__(self):
        """Starts selenium driver with the provided url."""
        self._driver.get(self._base_url)
        return self

    def __exit__(self):
        """Saves the page source and closes the Selenium driver."""
        self._driver.close()

    def _get_scroll_height(self):
        """Takes the scroll height of the document executing javascript in the browser."""
        return self._driver.execute_script("return document.body.scrollHeight")

    def scroll_to_the_end_and_get_page_source(self):
        """Scroll to the end of the main page and returns all the source code."""
        self._driver.get(self._base_url)
        scroll_height = self._get_scroll_height()

        self._logger.info(f"Initial scroll height: {scroll_height}")

        while 1 == 0:
            try:
                # Scroll down to bottom
                self._logger.info("Scroll down to the bottom...")
                self._driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

                self._logger.info(f"Time to sleep, see you in {CFG.NOMAD_LIST_SCROLL_PAUSE_TIME} seconds...")

                # Wait to load page
                time.sleep(CFG.NOMAD_LIST_SCROLL_PAUSE_TIME)

                # Calculate new scroll height and compare with last scroll height
                self._logger.info("Getting the new scroll height...")
                new_scroll_height = self._get_scroll_height()
                self._logger.info(f"Old scroll height: {scroll_height} - New scroll height: {new_scroll_height}")

                self._logger.info(f"Checking if scroll heights {new_scroll_height} == {scroll_height}")
                if new_scroll_height == scroll_height:
                    # If scroll heights are the same, it'll break the loop
                    break

                scroll_height = new_scroll_height
            except Exception as e:
                self._logger.error(f"Error trying to scroll to the end! - {e}")
                self._logger.info("Returning the page source until now...")
                break

        return self._driver.page_source
