import requests
from bs4 import BeautifulSoup
from conf import NOMAD_LIST_URL
from scrapper.city_scrapper import CityScrapper


class NomadListScrapper:
    """Class responsible to handle the scrapper in the Nomad List site."""

    def __init__(self):
        self._baseUrl = NOMAD_LIST_URL

    def get_cities(self):
        """
        Takes the cities from the home page, builds a dictionary for each one with the available information.
        Then, returns a list of dicts with all the cities.
        """
        home_page = self.get_home_page()
        soup = BeautifulSoup(home_page, "html.parser")

        return [CityScrapper().get_city_information(city_li) for city_li in soup.find_all(attrs={'data-type': 'city'})]

        return cities

    def get_home_page(self):
        """Tries to get the content of the home page."""
        response = requests.get(self._baseUrl)

        if response.status_code == requests.codes.ok:
            return response.content

        # TODO show nice error messages
        response.raise_for_status()
