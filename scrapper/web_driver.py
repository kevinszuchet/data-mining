from selenium import webdriver
import conf as CFG
import time


class WebDriver:
    def __init__(self, logger, base_url):
        self._base_url = base_url
        self._logger = logger
        self._logger.info('Initializing the web_driver')
        self._driver = webdriver.Chrome(CFG.CHROME_DRIVER_PATH) if CFG.CHROME_DRIVER_PATH else webdriver.Chrome()
        self._driver.get(self._base_url)

    def get_page_source(self):
        """Returns the Html file"""
        return self._driver.page_source

    def get_base_url(self):
        return self._driver.get(self._base_url)

    def close_driver(self):
        self._logger.info('Closing Driver')
        self._driver.quit()

    def _get_scroll_height(self):
        """Takes the scroll height of the document executing javascript in the browser."""
        return self._driver.execute_script("return document.body.scrollHeight")

    def scroll_to_the_end(self):
        """Scroll to the end of the main page and returns all the source code."""
        self._logger.info('Initializing Scrolling')
        self._driver.get(self._base_url)
        scroll_height = self._get_scroll_height()
        self._logger.info(f"Initial scroll height: {scroll_height}")
        self._logger.info("Scrolling down...")
        while True:
            try:
                # Scroll down to bottom
                self._driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

                # Wait to load page
                time.sleep(CFG.NOMAD_LIST_SCROLL_PAUSE_TIME)

                # Calculate new scroll height and compare with last scroll height
                new_scroll_height = self._get_scroll_height()
                if new_scroll_height == scroll_height and new_scroll_height > CFG.MINIMUM_SCROLL:
                    # If scroll heights are the same, it'll break the loop
                    break
                scroll_height = new_scroll_height
            except Exception as e:
                self._logger.error(f"Error trying to scroll to the end! - {e}")
                self._logger.info("Returning the page source until now...")
                break
        self._logger.info('Finished scrolling')

