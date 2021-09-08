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

SHOULD_USE_THE_HTML_FILE = os.getenv('ENV') != "production" and cfg.LOAD_HTML_FROM_DISK


class NomadListScrapper:
    """Class responsible to handle the scrapper in the Nomad List site."""

    def __init__(self, logger=None, web_driver=None, verbose=False):
        if logger is None:
            logger = Logger(verbose=verbose).logger

        if web_driver is None:
            web_driver = WebDriver(logger, cfg.NOMAD_LIST_URL)

        self._city_scrapper = CityScrapper(logger)

        self._driver = web_driver
        self._logger = logger

        self._verbose = verbose

    def _load_html_from_disk(self):
        """Attempts to load the html locally"""
        with open(cfg.PAGE_SOURCE, 'r') as opened_file:
            page_source = opened_file.read()
        return page_source

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
        if SHOULD_USE_THE_HTML_FILE and os.path.exists(cfg.PAGE_SOURCE):
            try:
                page_source = self._load_html_from_disk()
            except Exception as e:
                self._logger.error(f'There was an error loading the html file on path : {cfg.PAGE_SOURCE}. Error: {e}')
                page_source = self._driver.get_page_source(**kwargs)
        else:
            page_source = self._driver.get_page_source(**kwargs)

        if SHOULD_USE_THE_HTML_FILE:
            self._write_html_to_disk(page_source)
            self._logger.info('New Html written to disk')

        self._driver.close()
        return page_source

    def _get_cities(self, page_source, num_of_cities=None, **kwargs):
        """Scroll to the end of the main page fetching all the cities as li tags."""
        try:
            if page_source is None:
                self._logger.error('The website is None')
                return

            soup = BeautifulSoup(page_source, "html.parser")
            self._logger.debug(f"Created Beautiful soup object from the HTML file")
            list_of_cities_html = soup.find_all('li', attrs={'data-type': 'city'})
            self._logger.debug(f"Cities achieved")
            return list_of_cities_html if num_of_cities is None else list_of_cities_html[:num_of_cities]
        except(AttributeError, KeyError) as e:
            self._logger.error(f"Error trying to fetch the cities in the page source: {e}")
            sys.exit(1)

    def _fetch_details(self, lis):
        """Checks if the lis are valid, takes the valid ones and make the requests to the city details page.."""
        self._logger.debug(f'Number of Cities: {len(lis)}')
        self._logger.info(f"Fetching more info of the cities.... This might take time.")

        def _get_and_set_rank(city_li):
            return grequests.get(self._city_scrapper.get_city_url(city_li), headers=cfg.HEADERS, stream=False,
                                 callback=lambda r, **kwargs: self._set_rank(r, city_li))

        reqs = (_get_and_set_rank(li) for li in lis if self._city_scrapper.valid_tag(li))

        map_kwargs = {'size': cfg.NOMAD_LIST_REQUESTS_BATCH_SIZE, 'exception_handler': self._exception_handler}
        return grequests.imap(reqs, **map_kwargs)

    def _set_rank(self, r, city_li, **kwargs):
        """Given the response and a City Li, takes the rank of the main page, and set it as a response header."""
        r.headers.update({'rank': self._city_scrapper.get_rank(city_li)})
        return r

    def _exception_handler(self, req, error):
        """Logs the error of the requests."""
        self._logger.error(f"Error making the request {req.url}: {error}.\n The response was: {req.response}")

    def _map_details(self, res):
        """Try to get the details of the city using the content of the response. If the request failed,
        raises the appropriate an exception."""
        city_details_html = res.content
        self._logger.debug(f"The status code of {res.request.url} was {res.status_code}.")

        # Raises HTTPError, if one occurred.
        res.raise_for_status()

        return self._city_scrapper.get_city_details(res.headers.get('rank'), city_details_html)

    def scrap_cities(self, *args, **kwargs):
        """
        Takes the cities from the home page, builds a dictionary for each one with the available information.
        Then, returns a list of dicts with all the cities.
        """
        page_source = self._get_html(**kwargs)
        list_of_cities_html = self._get_cities(page_source, **kwargs)

        total = successes = failures = 0

        with MySQLConnector(logger=self._logger) as mysql_connector:
            for res in self._fetch_details(list_of_cities_html):
                try:
                    details = self._map_details(res)
                    res.close()

                    if details is None:
                        self._logger.info(f"Nothing to append with this city :(")
                        continue

                    self._logger.info(f"Storing new details...")
                    mysql_connector.insert_city_info(details)
                    successes += 1
                except HTTPError as e:
                    failures += 1
                    self._logger.error(f"HTTPError raised: {e}", exc_info=self._verbose)
                except Exception as e:
                    failures += 1
                    self._logger.error(f"Exception raised trying to get the city details: {e}", exc_info=self._verbose)
                finally:
                    total += 1

        self._logger.info(f"""
        Scrapping finished.
            - Total scrapped cities: {total}.
                - Successes: {successes}
                - Failures: {failures}
        """)
        return
