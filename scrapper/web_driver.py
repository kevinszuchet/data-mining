from selenium import webdriver
import conf as CFG
import time


# TODO Context Manager

class WebDriver:
    def __init__(self, logger, base_url):
        self._base_url = base_url
        self._logger = logger
        self._logger.info('Initializing the web_driver')
        self._driver = webdriver.Chrome(CFG.CHROME_DRIVER_PATH) if CFG.CHROME_DRIVER_PATH else webdriver.Chrome()

    def _get_scroll_height(self):
        """Takes the scroll height of the document executing javascript in the browser."""
        return self._driver.execute_script("return document.body.scrollHeight")

    def get_base_url(self):
        return self._driver.get(self._base_url)

    def close(self):
        self._logger.info('Closing Driver')
        self._driver.quit()

    def get_page_source(self, scrolls=None):
        """Scroll to the end of the main page and returns all the source code."""
        self._logger.info('Initializing Scrolling')
        self._driver.get(self._base_url)
        self._logger.info("Scrolling down...")
        # Get scroll height
        last_height = self._get_scroll_height()

        num_of_scrolls = 1

        while scrolls and scrolls <= num_of_scrolls:
            # Scroll down to bottom
            self._driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            self._logger.info(f"Scroll height: {last_height}")

            # Wait to load page
            time.sleep(CFG.NOMAD_LIST_SCROLL_PAUSE_TIME)

            # Calculate new scroll height and compare with last scroll height
            new_height = self._get_scroll_height()
            if new_height == last_height:
                break
            last_height = new_height
            num_of_scrolls += 1

        self._logger.info('Finished scrolling')

        return self._driver.page_source
