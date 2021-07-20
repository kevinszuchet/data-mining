import re
from scrapper.tab_scrapper import *
from logger import Logger


# TODO: is it ok if I change a method from static to non-static because of the logger?

class CityScrapper:
    """Class that knows how to get data from each city card."""
    action_regex = re.compile(r'(label|rating)-(\w+)-score')

    # To avoid cities lis with 'data-slug="{slugName}"'
    city_template_re = re.compile(r'{\w+}')

    def __init__(self):
        self._logger = Logger().logger

    def _get_tab_information(self, tab, city_details_soup):
        self._logger.info("Getting the tab information...")
        self._logger.debug(f"Tab: {tab}")
        tab_name = TabScrapper.tab_name(tab)
        self._logger.debug(f"Tab name: {tab_name}")
        dynamic_tab_scrapper = eval(f"{tab_name}TabScrapper")
        self._logger.debug(f"DynamicTabScrapper: {dynamic_tab_scrapper}")
        return dynamic_tab_scrapper(city_details_soup).get_information()

    def valid_tag(self, city_li):
        """Given the city li, checks if the tag is valid."""
        self._logger.debug(f"Validating the city li tag: {city_li}")
        if city_li is None:
            return False

        attrs = city_li.attrs
        self._logger.debug(f"Here they are... The city li attributes: {attrs}")
        return attrs.get('data-type') == 'city' and not CityScrapper.city_template_re.search(attrs.get('data-slug'))

    def get_city_url(self, city_li):
        """Given the city li, returns the url of it to go to the details."""
        a = city_li.find("a", attrs={'itemprop': 'url'})
        self._logger.debug(f"City li > a: {a}")
        if a:
            self._logger.debug(f"a > attrs: {a.attrs}")
            return a.attrs.get("href").strip()

    def get_city_details(self, city_details_html):
        """
        Given the city details html, takes all the available information about the city within the tabs.
        Then, returns a dict with all that information.
        """

        city_details_soup = BeautifulSoup(city_details_html, "html.parser")
        text = city_details_soup.find(class_="text")

        self._logger.debug(f"City details - <div class=\"text\">...<div>: {text}")

        if not text:
            return

        tabs = city_details_soup.find("div", class_="tabs").find("div", class_="ul").find_all("h2", class_="li")
        self._logger.debug(f"City details - Tabs: {tabs}")
        tabs_information = {TabScrapper.tab_name(tab): self._get_tab_information(tab, city_details_soup)
                            for tab in tabs if TabScrapper.valid_tab(tab)}

        self._logger.info("All tabs information was fetched!")

        return {
            'city': text.h1.text if text.h1 else "-",
            'country': text.h2.text if text.h2 else "-",
            **tabs_information
        }
