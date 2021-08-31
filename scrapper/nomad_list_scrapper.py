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

SHOULD_USE_THE_HTML_FILE = os.path.exists(cfg.PAGE_SOURCE) and os.getenv(
    'ENV') != "production" and cfg.LOAD_HTML_FROM_DISK


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

        self._verbose = verbose

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
        if SHOULD_USE_THE_HTML_FILE:
            page_source = self._load_html_from_disk()
        else:
            page_source = self._driver.get_page_source(**kwargs)
            if SHOULD_USE_THE_HTML_FILE:
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
        self._logger.info(f"Fetching more info of the cities.... This might take time.")
        req_kwargs = {'headers': cfg.HEADERS, 'stream': False}
        cities_urls = (grequests.get(f"{self._base_url}{self._city_scrapper.get_city_url(city_li)}", **req_kwargs)
                       for city_li in cities_lis if self._city_scrapper.valid_tag(city_li))
        return (grequests.map(cities_urls, size=cfg.NOMAD_LIST_REQUESTS_BATCH_SIZE,
                              exception_handler=self._exception_handler))

    def _get_city_details(self, res):
        """Try to get the details of the city using the content of the response. If the request failed,
        raises the appropriate an exception."""
        city_details_html = res.content
        self._logger.debug(f"The status code of {res.request.url} was {res.status_code}")
        # Raises HTTPError, if one occurred.
        res.raise_for_status()
        return self._city_scrapper.get_city_details(city_details_html)

    def _exception_handler(self, req, error):
        """Logs the error of the requests."""
        self._logger.error(f"Error making the request {req}: {error}")

    def scrap_cities(self, *args, **kwargs):
        """
        Takes the cities from the home page, builds a dictionary for each one with the available information.
        Then, returns a list of dicts with all the cities.
        """
        page_source = self._get_html(**kwargs)
        cities_lis = self._get_all_the_cities(page_source, **kwargs)

        with MySQLConnector(logger=self._logger) as mysql_connector:
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
                    self._logger.error(f"Exception raised trying to get the city details: {e}", exc_info=self._verbose)

        self._logger.info('Scrapping finished')
        return
