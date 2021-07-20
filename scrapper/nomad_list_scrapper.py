import sys

import requests
import time
from requests_futures.sessions import FuturesSession
from selenium import webdriver
from bs4 import BeautifulSoup
from conf import NOMAD_LIST_URL, NOMAD_LIST_SCROLL_PAUSE_TIME, PATH_TO_WEB_DRIVER
from scrapper.city_scrapper import CityScrapper
from concurrent.futures import as_completed
from logger import Logger


# TODO handle errors + logging


class NomadListScrapper:
    """Class responsible to handle the scrapper in the Nomad List site."""

    def __init__(self):
        self._baseUrl = NOMAD_LIST_URL
        self._driver = webdriver.Chrome(PATH_TO_WEB_DRIVER) if PATH_TO_WEB_DRIVER else webdriver.Chrome()
        # max_workers default value 8
        self._session = FuturesSession()
        self._logger = Logger().logger

    def _get_all_the_cities(self):
        """Scroll to the end of the main page fetching all the cities as li tags."""
        self._driver.get(self._baseUrl)
        scroll_height = self._get_scroll_height()

        self._logger.info("Initial scroll height:", scroll_height)

        while True:
            try:
                # Scroll down to bottom
                self._logger.info("Scroll down to the bottom...")
                self._driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

                self._logger.info(f"Time to sleep, see you in {NOMAD_LIST_SCROLL_PAUSE_TIME} seconds...")

                # Wait to load page
                time.sleep(NOMAD_LIST_SCROLL_PAUSE_TIME)

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
                self._logger.error("Error trying to scroll to the end!", e)
                self._logger.info("Getting all the cities fetched until now...")
                break

        page_source = self._driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")
        self._logger.debug("This is the pretty page source:", soup.prettify())
        self._driver.close()
        return soup.find_all('li', attrs={'data-type': 'city'})

    def _get_scroll_height(self):
        """Takes the scroll height of the document executing javascript in the browser."""
        return self._driver.execute_script("return document.body.scrollHeight")

    def _do_request(self, city_li):
        """Given the city li, takes the endpoint from the CityScrapper, and returns the result of making the request."""
        url = f"{self._baseUrl}{CityScrapper().get_city_url(city_li)}"
        html = self._session.get(url)
        self._logger.info(f"Request to {url} made, now is time to sleep...")
        time.sleep(5)
        return html

    def _make_request_to_city_details(self):
        """Checks if the lis are valid, takes the valid ones and make the requests to the city details page."""
        return (self._do_request(li) for li in self._get_all_the_cities() if CityScrapper().valid_tag(li))

    def _get_city_details(self, future):
        res = future.result()
        self._logger.debug(f"City Details GET - Status Code: {res.status_code}")
        city_details_html = res.content
        return CityScrapper().get_city_details(city_details_html)

    def get_cities(self):
        """
        Takes the cities from the home page, builds a dictionary for each one with the available information.
        Then, returns a list of dicts with all the cities.
        """
        try:
            futures = self._make_request_to_city_details()
            return [self._get_city_details(future) for future in as_completed(futures)]
        except Exception as e:
            self._logger.error(f"Exception: {e}")
