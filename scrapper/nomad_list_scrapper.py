import requests
import time
from requests_futures.sessions import FuturesSession
from selenium import webdriver
from bs4 import BeautifulSoup
from conf import NOMAD_LIST_URL, NOMAD_LIST_SCROLL_PAUSE_TIME
from scrapper.city_scrapper import CityScrapper
from concurrent.futures import as_completed


# TODO use logging


class NomadListScrapper:
    """Class responsible to handle the scrapper in the Nomad List site."""

    def __init__(self):
        self._baseUrl = NOMAD_LIST_URL
        self._driver = webdriver.Chrome()
        # max_workers default value 8
        self._session = FuturesSession()

    def _get_all_the_cities(self):
        self._driver.get(self._baseUrl)
        scroll_height = self._get_scroll_height()

        print("Initial scroll height:", scroll_height)

        while True:
            try:
                # Scroll down to bottom
                print("Scroll down to the bottom...")
                self._driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

                print(f"Time to sleep, see you in {NOMAD_LIST_SCROLL_PAUSE_TIME} seconds...")

                # Wait to load page
                time.sleep(NOMAD_LIST_SCROLL_PAUSE_TIME)

                # Calculate new scroll height and compare with last scroll height
                print("Getting the new scroll height...")
                new_scroll_height = self._get_scroll_height()
                print(f"Old scroll height: {scroll_height} - New scroll height: {new_scroll_height}")

                print(f"Checking if scroll heights {new_scroll_height} == {scroll_height}")
                if new_scroll_height == scroll_height:
                    # If scroll heights are the same, it'll break the loop
                    break

                scroll_height = new_scroll_height
            except Exception as e:
                print("Error trying to scroll to the end!", e)
                print("Getting all the cities fetched until now...")
                break
                # raise e

        page_source = self._driver.page_source
        # This is only for debugging
        print("This is the page source:", page_source)
        soup = BeautifulSoup(page_source, "html.parser")
        return soup.find_all(attrs={'data-type': 'city'})

    def _get_scroll_height(self):
        """Takes the scroll height of the document executing javascript in the browser."""
        return self._driver.execute_script("return document.body.scrollHeight")

    def _get_city_details(self, city_li):
        """Given the city li, takes the endpoint from the CityScrapper, and returns the result of making the request."""
        url = f"{self._baseUrl}{CityScrapper.get_city_url(city_li)}"
        return self._session.get(url)

    def get_cities(self):
        """
        Takes the cities from the home page, builds a dictionary for each one with the available information.
        Then, returns a list of dicts with all the cities.
        """
        futures = (self._get_city_details(city_li) for city_li in self._get_all_the_cities())
        # TODO handle errors
        return [CityScrapper().get_city_details(future.result().content) for future in as_completed(futures)]
