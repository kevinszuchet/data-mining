import time
import conf as CFG
from selenium import webdriver


# TODO Context Manager

class Scroller:
    """Class responsible to scroll web sites."""

    def __init__(self, site_url, logger):
        self._base_url = site_url
        self._driver = webdriver.Chrome(CFG.CHROME_DRIVER_PATH) if CFG.CHROME_DRIVER_PATH else webdriver.Chrome()
        self._logger = logger

    def scroll_and_get_the_source_code(self):
        """Scroll to the end of the main page and returns all the source code."""
        self._driver.get(self._base_url)
        scroll_height = self._get_scroll_height()

        self._logger.info(f"Initial scroll height: {scroll_height}")

        while True:
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

        page_source = self._driver.page_source
        self._driver.close()
        return page_source

    def _get_scroll_height(self):
        """Takes the scroll height of the document executing javascript in the browser."""
        return self._driver.execute_script("return document.body.scrollHeight")
