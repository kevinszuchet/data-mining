import grequests
import time
import conf as CFG
import os
from requests import HTTPError
from bs4 import BeautifulSoup
from scrapper.city_scrapper import CityScrapper
import sys

# TODO Adapter for Selenium Web Drivers + Context Manager


class NomadListScrapper:
    """Class responsible to handle the scrapper in the Nomad List site."""

    def __init__(self, logger, web_driver):
        self._base_url = CFG.NOMAD_LIST_URL
        self._driver = web_driver
        self._logger = logger

        # Information after scrapping
        self._cities = []

        # Beautiful soup
        self._cities_lis = None

        # David's
        self._cities_details = None
        self._city_scrapper = CityScrapper(self._logger)
        self.page = None
        self.get_cities()

    def get_cities_info(self):
        return self._cities

    def load_html_from_disk(self):
        """Attempts to load the html locally"""
        try:
            with open(CFG.PAGE_SOURCE, 'r') as opened_file:
                self.page = opened_file.read()
        except Exception as e:
            self._logger.error(f'There was an error loading the html file on path : {CFG.PAGE_SOURCE}. Error: {e}')
            sys.exit(1)

    def write_html_to_disk(self):
        try:
            with open(CFG.PAGE_SOURCE, 'w+') as opened_file:
                opened_file.write(self.page)
        except Exception as e:
            self._logger.error(f'There was an error writing the html file on path : {CFG.PAGE_SOURCE}. Error: {e}')
            sys.exit(1)

    def fetch_website(self):
        """Fetches the main website HTML"""
        # Scroll to the end to add more cities
        if CFG.SCROLL:
            self._driver.scroll_to_the_end()
        self.page = self._driver.get_page_source()

    def _get_html(self):
        """Gets the Main HTML file which contents will be scrapped"""
        self._logger.info('Retrieving base Html file')
        if os.path.exists(CFG.PAGE_SOURCE) and os.getenv('ENV') != "production" and CFG.LOAD_HTML_FROM_DISK:
            self.load_html_from_disk()
        else:
            self.fetch_website()
            self.write_html_to_disk()

    def _get_all_the_cities(self):
        """Scroll to the end of the main page fetching all the cities as li tags."""
        try:
            if self.page is None:
                self._logger.error('The website is None')
                return

            soup = BeautifulSoup(self.page, "html.parser")
            self._logger.debug(f"Created Beautiful soup object from the HTML file")
            cities_lis = soup.find_all('li', attrs={'data-type': 'city'})
            self._logger.debug(f"Cities achieved")
            self._cities_lis = cities_lis
        except(AttributeError, KeyError) as e:
            self._logger.error(f"Error trying to find all the cities in the page source: {e}")
            sys.exit(1)

    def _do_request(self, city_li):
        """Given the city li, takes the endpoint from the CityScrapper, and returns the result of making the request."""
        url = f"{self._base_url}{self._city_scrapper.get_city_url(city_li)}"
        res = grequests.get(url, headers=CFG.HEADERS)
        self._logger.info(f"Request to {url} made, now is time to sleep before the next one...")
        time.sleep(CFG.NOMAD_LIST_DELAY_AFTER_REQUEST)
        return res

    def _make_request_to_city_details(self):
        """Checks if the lis are valid, takes the valid ones and make the requests to the city details page."""
        self._logger.debug(f'amount of Cities: {len(self._cities_lis)}')
        self._logger.debug(f"Fetching more info for the cities")
        city_details = (self._do_request(li) for li in self._cities_lis if self._city_scrapper.valid_tag(li))
        self._cities_details = city_details
        self._logger.debug(f"More details fetched")

    def _get_city_details(self, res):
        city_details_html = res.content
        self._logger.info(f"The status code of {res.request.url} was {res.status_code}")
        # Raises HTTPError, if one occurred.
        res.raise_for_status()
        return self._city_scrapper.get_city_details(city_details_html)

    def _exception_handler(self, req, error):
        self._logger.error(f"Error making the request {req}: {error}")

    def get_cities(self):
        """
        Takes the cities from the home page, builds a dictionary for each one with the available information.
        Then, returns a list of dicts with all the cities.
        """
        self._get_html()
        self._get_all_the_cities()
        self._make_request_to_city_details()

        for res in grequests.map(self._cities_details, size=CFG.NOMAD_LIST_REQUESTS_BATCH_SIZE,
                                 exception_handler=self._exception_handler):
            try:
                details = self._get_city_details(res)
                if details is None:
                    self._logger.info(f"Nothing to append with this city :(")
                    break
                self._logger.info(f"Appending new details... {details}")
                self._cities.append(details)
            except HTTPError as e:
                self._logger.error(f"HTTPError raised: {e}")
            except Exception as e:
                self._logger.error(f"Exception raised trying to get the city details: {e}")
        self._driver.close_driver()
        self._logger.info('Scrapping finished')
        return
