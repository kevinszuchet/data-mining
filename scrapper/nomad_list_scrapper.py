import grequests
import conf as cfg
import os
from requests import HTTPError
from bs4 import BeautifulSoup
from scrapper.city_scrapper import CityScrapper
from db.mysql_connector import MySQLConnector
import sys
from logger import Logger
from scrapper.web_driver import WebDriver


class NomadListScrapper:
    """Class responsible to handle the scrapper in the Nomad List site."""

    def __init__(self, logger=None, web_driver=None, verbose=False):
        if logger is None:
            logger = Logger(verbose=verbose).logger

        if web_driver is None:
            web_driver = WebDriver(logger, cfg.NOMAD_LIST_URL)

        self._base_url = cfg.NOMAD_LIST_URL
        self._driver = web_driver
        self._logger = logger

        # Beautiful soup
        self._cities_lis = None

        self._city_scrapper = CityScrapper(self._logger)

    def _load_html_from_disk(self):
        """Attempts to load the html locally"""
        try:
            with open(cfg.PAGE_SOURCE, 'r') as opened_file:
                page_source = opened_file.read()
            return page_source
        except Exception as e:
            self._logger.error(f'There was an error loading the html file on path : {cfg.PAGE_SOURCE}. Error: {e}')
            sys.exit(1)

    def _write_html_to_disk(self, page_source):
        try:
            with open(cfg.PAGE_SOURCE, 'w+') as opened_file:
                opened_file.write(page_source)
        except Exception as e:
            self._logger.error(f'There was an error writing the html file on path : {cfg.PAGE_SOURCE}. Error: {e}')
            sys.exit(1)

    def _get_html(self, **kwargs):
        """Gets the Main HTML file which contents will be scrapped"""
        self._logger.info('Retrieving base Html file')
        should_fetch_and_dump_from_disk = os.path.exists(cfg.PAGE_SOURCE) and os.getenv(
            'ENV') != "production" and cfg.LOAD_HTML_FROM_DISK
        if should_fetch_and_dump_from_disk:
            page_source = self._load_html_from_disk()
        else:
            page_source = self._driver.get_page_source(**kwargs)
            if should_fetch_and_dump_from_disk:
                self._write_html_to_disk(page_source)
                self._logger.info('New Html written to disk')

        self._driver.close()
        return page_source

    def _get_all_the_cities(self, page_source, num_of_cities=None, **kwargs):
        """Scroll to the end of the main page fetching all the cities as li tags."""
        try:
            if page_source is None:
                self._logger.error('The website is None')
                return

            soup = BeautifulSoup(page_source, "html.parser")
            self._logger.debug(f"Created Beautiful soup object from the HTML file")
            cities_lis = soup.find_all('li', attrs={'data-type': 'city'})
            self._logger.debug(f"Cities achieved")
            return cities_lis if num_of_cities is None else cities_lis[:num_of_cities]
        except(AttributeError, KeyError) as e:
            self._logger.error(f"Error trying to find all the cities in the page source: {e}")
            sys.exit(1)

    def _requests_to_city_details(self, cities_lis):
        """Checks if the lis are valid, takes the valid ones and make the requests to the city details page."""
        self._logger.debug(f'Number of Cities: {len(cities_lis)}')
        self._logger.debug(f"Fetching more info for the cities.... This might take time.")
        cities_urls = (
            grequests.get(f"{self._base_url}{self._city_scrapper.get_city_url(x)}", headers=cfg.HEADERS, stream=False)
            for x in cities_lis if self._city_scrapper.valid_tag(x))
        return (grequests.map(cities_urls, size=cfg.NOMAD_LIST_REQUESTS_BATCH_SIZE,
                              exception_handler=self._exception_handler))

    def _get_city_details(self, res):
        city_details_html = res.content
        self._logger.info(f"The status code of {res.request.url} was {res.status_code}")
        # Raises HTTPError, if one occurred.
        res.raise_for_status()
        return self._city_scrapper.get_city_details(city_details_html)

    def _exception_handler(self, req, error):
        self._logger.error(f"Error making the request {req}: {error}")

    def scrap_cities(self, *args, **kwargs):
        """
        Takes the cities from the home page, builds a dictionary for each one with the available information.
        Then, returns a list of dicts with all the cities.
        """
        page_source = self._get_html(**kwargs)
        cities_lis = self._get_all_the_cities(page_source, **kwargs)

        mysql_connector = MySQLConnector(self._logger)

        for res in self._requests_to_city_details(cities_lis):
            try:
                details = self._get_city_details(res)
                res.close()
                if details is None:
                    self._logger.info(f"Nothing to append with this city :(")
                    break
                self._logger.info(f"Storing new details...")
                mysql_connector.insert_city_info(details)
            except HTTPError as e:
                self._logger.error(f"HTTPError raised: {e}")
            except Exception as e:
                # TODO: remove exc_info
                self._logger.error(f"Exception raised trying to get the city details: {e}", exc_info=True)
        self._logger.info('Scrapping finished')
        return
