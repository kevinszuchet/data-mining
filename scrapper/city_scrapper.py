import re
import conf as cfg
from .tab_scrapper import *
from bs4 import BeautifulSoup


class CityScrapper:
    """Class that knows how to get data from each city."""
    # To avoid cities lis with 'data-slug="{slugName}"'
    city_template_re = re.compile(r'{\w+}')

    def __init__(self, logger):
        self._logger = logger
        self._base_url = cfg.NOMAD_LIST_URL

    def _get_tab_information(self, tab, city_details_soup):
        """
        Given the tab and the soup object, dynamically builds a tab scrapper that depends on the name of the tab,
        and gets all the information of it. Then, returns that information as a dict "{tab_name: tab_information}"
        """
        tab_name = TabScrapper.get_name(tab)
        self._logger.info(f"Getting the {tab_name} tab information...")
        self._logger.debug(f"Tab with name {tab_name}: {tab}")
        dynamic_tab_scrapper = eval(f"{tab_name}TabScrapper")
        self._logger.debug(f"DynamicTabScrapper: {dynamic_tab_scrapper}")
        return dynamic_tab_scrapper(city_details_soup, logger=self._logger).get_information()

    def _get_aviation_stack_country_info(self, country, aviation_stack_countries):
        aviation_stack_country = aviation_stack_countries.get(country)

        if not aviation_stack_country:
            return {}

        return {
            'iso2': aviation_stack_country.get("country_iso2"),
            'iso3': aviation_stack_country.get("country_iso3"),
            'iso_numeric': aviation_stack_country.get("country_iso_numeric"),
            'population': aviation_stack_country.get("population"),
            'currency': {
                'name': aviation_stack_country.get("currency_name"),
                'code': aviation_stack_country.get("currency_code")
            },
            'fips_code': aviation_stack_country.get("fips_code"),
            'phone_prefix': aviation_stack_country.get("phone_prefix")
        }

    def _get_aviation_stack_city_info(self, city, aviation_stack_cities):
        aviation_stack_city = aviation_stack_cities.get(city)

        if not aviation_stack_city:
            return {}

        return {
            'iata_code': aviation_stack_city.get("iata_code"),
            'latitude': aviation_stack_city.get("latitude"),
            'longitude': aviation_stack_city.get("longitude"),
            'timezone': aviation_stack_city.get("timezone"),
            'gmt': aviation_stack_city.get("gmt"),
            'geoname_id': aviation_stack_city.get("geoname_id")
        }

    def valid_tag(self, city_li):
        """Given the city li, checks if the tag is valid."""
        if city_li is None:
            return False

        attrs = city_li.attrs
        self._logger.debug(f"Validating the city li tag: {attrs}")
        city_url = self.get_city_url(city_li)
        self._logger.debug(f"City li url: {city_url}")
        return attrs.get('data-type') == 'city' and not CityScrapper.city_template_re.search(attrs.get('data-slug')) \
               and city_url is not None

    def get_city_url(self, city_li):
        """Given the city li, returns the url of it to go to the details."""
        try:
            a = city_li.find("a")
            if a:
                return f"{self._base_url}{a.attrs.get('href').strip()}"
        except(AttributeError, KeyError) as e:
            self._logger.error(f"Error trying to get the city url {e}")

    def get_city_details(self, city_details_html, aviation_stack_countries, aviation_stack_cities):
        """
        Given the city details html, takes all the available information about the city within the tabs.
        Then, returns a dict with all that information.
        """
        try:
            city_details_soup = BeautifulSoup(city_details_html, "html.parser")
            text = city_details_soup.find(class_="text")

            if not text:
                return

            city = text.h1.text if text.h1 else "-"
            country = text.h2.text if text.h2 else "-"
            # TODO we have problems with the data-i of the cities. It should be the rank but,
            #  after 26 cities, it always brings the same value (data-i="26").
            rank = int(ScoresTabScrapper(city_details_soup).get_rank())

            self._logger.info(f'Fetching the info of {city}, {country} with rank #{rank}')

            tabs = city_details_soup.find("div", class_="tabs").find("div", class_="ul").find_all("h2", class_="li")
            self._logger.debug(f"{city}, {country} tabs: {tabs}")
            tabs_information = {TabScrapper.get_name(tab): self._get_tab_information(tab, city_details_soup)
                                for tab in tabs if TabScrapper.is_valid(tab)}

            self._logger.info(f"All the information about {city}, {country} was fetched!")

            return {
                'city': city,
                'country': {
                    'name': country,
                    **self._get_aviation_stack_country_info(country, aviation_stack_countries),
                },
                'continent': DigitalNomadGuideTabScrapper(city_details_soup).get_continent(),
                'rank': rank,
                **self._get_aviation_stack_city_info(city, aviation_stack_cities),
                **tabs_information
            }
        except(AttributeError, KeyError) as e:
            self._logger.error(f"Error trying to get the city details: {e}")
