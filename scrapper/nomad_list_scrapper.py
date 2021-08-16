import grequests
import conf as CFG
import os
from requests import HTTPError
from bs4 import BeautifulSoup
from scrapper.city_scrapper import CityScrapper
import sys


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

        # TODO ???????
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
            self._logger.info('New Html written to disk')

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

    def _make_request_to_city_details(self):
        """Checks if the lis are valid, takes the valid ones and make the requests to the city details page."""
        self._logger.debug(f'Number of Cities: {len(self._cities_lis)}')
        self._logger.debug(f"Fetching more info for the cities.... This might take time.")
        cities_urls = (
            grequests.get(f"{self._base_url}{self._city_scrapper.get_city_url(x)}", headers=CFG.HEADERS, stream=False)
            for x in self._cities_lis if self._city_scrapper.valid_tag(x))
        self._cities_details = (grequests.map(cities_urls, size=CFG.NOMAD_LIST_REQUESTS_BATCH_SIZE,
                                              exception_handler=self._exception_handler))
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

        for res in self._cities_details:
            try:
                details = self._get_city_details(res)
                res.close()
                if details is None:
                    self._logger.info(f"Nothing to append with this city :(")
                    break
                self._logger.info(f"Appending new details...")
                self._cities.append(details)
            except HTTPError as e:
                self._logger.error(f"HTTPError raised: {e}")
            except Exception as e:
                self._logger.error(f"Exception raised trying to get the city details: {e}")
        self._driver.close()
        self._logger.info('Scrapping finished')
        return
