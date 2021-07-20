import re
from bs4 import BeautifulSoup
from scrapper.tab_scrapper import TabScrapper, CostOfLivingTabScrapper, DigitalNomadGuideTabScrapper, \
    ProsAndConsTabScrapper, ReviewsTabScrapper, ScoresTabScrapper, WeatherTabScrapper


class CityScrapper:
    """Class that knows how to get data from each city card."""
    action_regex = re.compile(r'(label|rating)-(\w+)-score')

    # To avoid cities lis with 'data-slug="{slugName}"'
    city_template_re = re.compile(r'{\w+}')

    @staticmethod
    def valid_tag(city_li):
        """Given the city li, checks if the tag is valid."""
        attrs = city_li.attrs
        return attrs.get('data-type') == 'city' and not CityScrapper.city_template_re.search(attrs.get('data-slug'))

    @staticmethod
    def get_city_url(city_li):
        """Given the city li, returns the url of it to go to the details."""
        a = city_li.find("a", attrs={'itemprop': 'url'})
        return a.attrs.get("href").strip()

    def _get_tab_information(self, tab, city_details_soup):
        tab_name = TabScrapper.tab_name(tab)
        return eval(f"{tab_name}TabScrapper")(city_details_soup).get_information()

    def get_city_details(self, city_details_html):
        """
        Given the city details html, takes all the available information about the city within the tabs.
        Then, returns a dict with all that information.
        """

        city_details_soup = BeautifulSoup(city_details_html, "html.parser")
        text = city_details_soup.find(class_="text")

        if not text:
            return

        tas_tags = city_details_soup.find("div", class_="tabs").find("div", class_="ul").find_all("h2", class_="li")
        tabs_information = {TabScrapper.tab_name(tab): self._get_tab_information(tab, city_details_soup)
                            for tab in tas_tags if TabScrapper.valid_tab(tab)}

        return {
            'city': text.h1.text if text.h1 else "-",
            'country': text.h2.text if text.h2 else "-",
            **tabs_information
        }
