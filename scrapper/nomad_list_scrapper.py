import grequests
import time
import conf as CFG
import os
from requests import HTTPError
from selenium import webdriver
from bs4 import BeautifulSoup
from scrapper.city_scrapper import CityScrapper

# TODO Adapter for Selenium Web Drivers + Context Manager

headers = {
    'user-agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36",
    'cookie': "ref=weremoto; visit-count=1; last_tested_internet_speed=2020-03-13_x; __stripe_mid=0adfa558-f217-49fe-8f7c-7c769760f498b8f7c4; visit-count=2; login_by_email_client_hash=6e693f5e751a957575c6c6bd664bba4a; login_url=https://nomadlist.com/?join=nomadlist; logged_in_hash=fccb1ad6e406b0111d55512cad8ae099_4885b578c08d502e2c6b6ae23d523bb26949c16e; ask_to_connect_instagram_hide=x; filters-folded=no; dark_mode=on; dark_mode_js_test=on; PHPSESSID=nba5obbj3eb9qn9pe2ch25evi1; last_tested_internet_speed=2021-07-25_x"
}


class NomadListScrapper:
    """Class responsible to handle the scrapper in the Nomad List site."""

    def __init__(self, logger):
        self._base_url = CFG.NOMAD_LIST_URL
        self._driver = webdriver.Chrome(CFG.CHROME_DRIVER_PATH) if CFG.CHROME_DRIVER_PATH else webdriver.Chrome()
        self._logger = logger
        self._city_scrapper = CityScrapper(self._logger)

    def _get_all_the_cities(self):
        """Scroll to the end of the main page fetching all the cities as li tags."""
        if os.path.exists("page_source.html") and os.getenv('ENV') != "production":
            with open("page_source.html", 'r') as opened_file:
                page_source = opened_file.read()
        else:
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
                    self._logger.info("Getting all the cities fetched until now...")
                    break

            page_source = self._driver.page_source
            with open("page_source.html", 'w+') as opened_file:
                opened_file.write(page_source)

        soup = BeautifulSoup(page_source, "html.parser")
        self._logger.debug(f"This is the pretty page source: {soup.prettify()}")
        self._driver.close()
        cities_lis = soup.find_all('li', attrs={'data-type': 'city'})
        self._logger.debug(f"Cities lis: {cities_lis}")
        return cities_lis

    def _get_scroll_height(self):
        """Takes the scroll height of the document executing javascript in the browser."""
        return self._driver.execute_script("return document.body.scrollHeight")

    def _do_request(self, city_li):
        """Given the city li, takes the endpoint from the CityScrapper, and returns the result of making the request."""
        url = f"{self._base_url}{self._city_scrapper.get_city_url(city_li)}"
        res = grequests.get(url, headers=headers)
        self._logger.info(f"Request to {url} made, now is time to sleep before the next one...")
        time.sleep(CFG.NOMAD_LIST_DELAY_AFTER_REQUEST)
        return res

    def _make_request_to_city_details(self):
        """Checks if the lis are valid, takes the valid ones and make the requests to the city details page."""
        return (self._do_request(li) for li in self._get_all_the_cities() if self._city_scrapper.valid_tag(li))

    def _get_city_details(self, res):
        city_details_html = res.content
        self._logger.info(f"The status code of {res.request.url} was {res.status_code}")
        # Raises HTTPError, if one occurred.
        res.raise_for_status()
        return self._city_scrapper.get_city_details(city_details_html)

    def get_cities(self):
        """
        Takes the cities from the home page, builds a dictionary for each one with the available information.
        Then, returns a list of dicts with all the cities.
        """
        cities = []
        for res in grequests.map(self._make_request_to_city_details(), size=CFG.NOMAD_LIST_REQUESTS_BATCH_SIZE):
            try:
                details = self._get_city_details(res)
                self._logger.info(f"Appending new details... {details}")
                cities.append(details)
            except HTTPError as e:
                self._logger.error(f"HTTPError raised: {e}")
            except Exception as e:
                self._logger.error(f"Exception raised trying to get the city details: {e}")
        return cities
