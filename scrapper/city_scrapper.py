import re
from .tab_scrapper import *
from bs4 import BeautifulSoup

# TODO: is it ok if I change a method from static to non-static because of the logger?


class CityScrapper:
    """Class that knows how to get data from each city card."""
    action_regex = re.compile(r'(label|rating)-(\w+)-score')

    # To avoid cities lis with 'data-slug="{slugName}"'
    city_template_re = re.compile(r'{\w+}')

    def __init__(self, logger):
        self._logger = logger

    def _get_tab_information(self, tab, city_details_soup):
        self._logger.info("Getting the tab information...")
        self._logger.debug(f"Tab: {tab}")
        tab_name = TabScrapper.get_name(tab)
        self._logger.debug(f"Tab name: {tab_name}")
        dynamic_tab_scrapper = eval(f"{tab_name}TabScrapper")
        self._logger.debug(f"DynamicTabScrapper: {dynamic_tab_scrapper}")
        return dynamic_tab_scrapper(city_details_soup, logger=self._logger).get_information()

    def valid_tag(self, city_li):
        """Given the city li, checks if the tag is valid."""
        self._logger.debug(f"Validating the city li tag: {city_li.prettify()}")
        if city_li is None:
            return False

        attrs = city_li.attrs
        city_url = self.get_city_url(city_li)
        self._logger.debug(f"City li url: {city_url}")
        return attrs.get('data-type') == 'city' and not CityScrapper.city_template_re.search(attrs.get('data-slug')) \
               and city_url is not None

    def get_city_url(self, city_li):
        """Given the city li, returns the url of it to go to the details."""
        try:
            a = city_li.find("a")
            if a:
                return a.attrs.get("href").strip()
        except(AttributeError, KeyError) as e:
            self._logger.error(f"Error trying to get the city url {e}")

    def get_city_details(self, city_details_html):
        """
        Given the city details html, takes all the available information about the city within the tabs.
        Then, returns a dict with all that information.
        """
        try:
            city_details_soup = BeautifulSoup(city_details_html, "html.parser")
            text = city_details_soup.find(class_="text")

            self._logger.debug(f"City details - <div class=\"text\">...<div>: {text}")

            if not text:
                return

            city = text.h1.text if text.h1 else "-"
            country = text.h2.text if text.h2 else "-"

            tabs = city_details_soup.find("div", class_="tabs").find("div", class_="ul").find_all("h2", class_="li")
            self._logger.debug(f"City details - Tabs: {tabs}")
            tabs_information = {TabScrapper.get_name(tab): self._get_tab_information(tab, city_details_soup)
                                for tab in tabs if TabScrapper.is_valid(tab)}
            self._logger.debug(f"City details - Tabs Information: {tabs_information}")

            self._logger.info(f"All the information about {city}, {country} was fetched!")

            # TODO get the rank

            return {
                'city': city,
                'country': country,
                **tabs_information
            }
        except(AttributeError, KeyError) as e:
            print(e)


