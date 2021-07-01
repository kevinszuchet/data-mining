import re
import requests
from bs4 import BeautifulSoup
from conf import NOMAD_LIST_URL


class NomadListScrapper:
    """Class responsible to handle the scrapper in the Nomad List site."""
    def __init__(self):
        self._baseUrl = NOMAD_LIST_URL

    def get_home_page(self):
        response = requests.get(self._baseUrl)

        if response.status_code == requests.codes.ok:
            return response.content

        # TODO show nice error messages
        response.raise_for_status()

    def get_cities(self):
        """
        Takes the cities from the home page, builds a dictionary for each one with the available information.
        Then, returns a list of dicts with all the cities.
        """
        cities = []
        home_page = self.get_home_page()
        soup = BeautifulSoup(home_page, "html.parser")

        for li in soup.find_all(attrs={'data-type': 'city'}):
            print(li)

        return cities
