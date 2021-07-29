import re
from .tab_scrapper import *
from bs4 import BeautifulSoup


class CityScrapper:
    """Class that knows how to get data from each city."""
    # To avoid cities lis with 'data-slug="{slugName}"'
    city_template_re = re.compile(r'{\w+}')

    # Rank regex
    rank_re = re.compile(r'.*\(Rank #(\d+)\).*')

    def __init__(self, logger):
        self._logger = logger

    def _get_tab_information(self, tab, city_details_soup):
        """
        Given the tab and the soup object, dynamically builds a tab scrapper that depends on the name of the tab,
        and gets all the information of it. Then, returns that information as a dict "{tab_name: tab_information}"
        """
        # self._logger.info("Getting the tab information...")
        tab_name = TabScrapper.get_name(tab)
        # self._logger.debug(f"Tab with name {tab_name}: {tab}")
        dynamic_tab_scrapper = eval(f"{tab_name}TabScrapper")
        # self._logger.debug(f"DynamicTabScrapper: {dynamic_tab_scrapper}")
        return dynamic_tab_scrapper(city_details_soup, logger=self._logger).get_information()

    def valid_tag(self, city_li):
        """Given the city li, checks if the tag is valid."""
        # self._logger.debug(f"Validating the city li tag: {city_li.prettify()}")
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
            # self._logger.debug(f"City details - <div class=\"text\">...<div>: {text}")

            if not text:
                return
            self._logger.info('Fetching tabs info...')
            city = text.h1.text if text.h1 else "-"
            country = text.h2.text if text.h2 else "-"

            tabs = city_details_soup.find("div", class_="tabs").find("div", class_="ul").find_all("h2", class_="li")
            # self._logger.debug(f"City details - Tabs: {tabs}")
            tabs_information = {TabScrapper.get_name(tab): self._get_tab_information(tab, city_details_soup)
                                for tab in tabs if TabScrapper.is_valid(tab)}
            # self._logger.debug(f"City details - Tabs Information: {tabs_information}")
            # self._logger.info(f"All the information about {city}, {country} was fetched!")

            scores_tab = city_details_soup.find("div", class_="tab tab-ranking show")
            scores_details = scores_tab.find("table", class_="details")
            rank, = self.rank_re.match(scores_details.find("td", class_="value").get_text()).groups()

            return {
                'city': city,
                'country': country,
                'rank': int(rank),
                **tabs_information
            }
        except(AttributeError, KeyError) as e:
            self._logger.error(f"Error trying to get the city details: {e}")
