import time
import re
import itertools
import requests as rq
from bs4 import BeautifulSoup
from logger import Logger

LATIN1_NON_BREAKING_SPACE = u'\xa0'


class TabScrapper:
    """
    Generic TabScrapper class. Is the father of all the other implementations. It knows how to return the name of the
    tab and how to valid the html tag.
    """

    def __init__(self, soup, logger=None):
        container = soup.find("div", class_="tab-scroller-container")
        self._tab_scroller = container.find("div", class_="tab-scroller")
        if logger is None:
            logger = Logger().logger
        self._logger = logger

    @staticmethod
    def get_name(tab):
        """Given the html tag of the tab, returns the name of the tab."""
        return tab.find("a").get_text(strip=True).title().replace(' ', '')

    @staticmethod
    def is_valid(tab):
        """
        Given the tag of the tab, dynamically initialize a new concrete tab scrapper,
        and checks if it's a valid subclass.
        """
        try:
            dynamic_tab_scrapper = eval(f"{TabScrapper.get_name(tab)}TabScrapper")
        except NameError:
            return False
        else:
            return issubclass(dynamic_tab_scrapper, TabScrapper)

    def _get_information(self):
        """Abstract method that all the subclasses have to override."""
        pass

    def get_information(self):
        """Returns the information of the tab using the implementation of the concrete classes."""
        try:
            return self._get_information()
        except(AttributeError, KeyError) as e:
            self._logger.error(f"Error scrapping the tab information: {e}")


class KeyValueTabScrapper(TabScrapper):
    """Class that knows how to handle tabs with a structure of <tr><td class="key"></td><td class="value"></td></tr>."""

    def _get_key(self, key_column):
        """Given the key column it takes and returns the text of the column."""
        return key_column.text.replace(u'\xa0', u' ')

    def _get_value(self, value_column):
        """Given the value column it takes and returns the text of the column."""
        pass

    def _get_information(self):
        """
        Iterates over all the rows in the table, builds a dict with the keys and values columns and, returns the dict.
        """
        info_dict = {}
        table = self._tab.find('table', class_='details')
        for row in table.find_all('tr'):
            row_key, row_value = row.find(class_='key'), row.find(class_='value')
            key_with_emoji, value = self._get_key(row_key), self._get_value(row_value)
            split_key = key_with_emoji.split(" ", 1)

            if len(split_key):
                key = split_key[-1]
                info_dict.update({key: value})

        return info_dict


class ScoresTabScrapper(KeyValueTabScrapper):
    """Class that knows how to scrap the data from the Scores tab."""

    # Rank regex
    rank_re = re.compile(r'.*\(Rank #(\d+)\).*')

    def __init__(self, soup, **kwargs):
        super().__init__(soup, **kwargs)
        self._tab = self._tab_scroller.find("div", class_="tab tab-ranking show")

    def _get_value(self, value_column):
        """Override the super class method. Given the value column it takes and returns the text of the value."""
        return value_column.div.div.text, self.get_bar_value(value_column)

    def get_rank(self):
        """Given the city details soup, knows how to take the rank number."""
        details = self._tab.find("table", class_="details")
        rank, = self.rank_re.match(details.find("td", class_="value").get_text()).groups()
        return rank

    def get_bar_value(self, value_column):
        """Given the city details soup, knows how to take the percentage that the bar is filled."""
        style = value_column.div.find("div", attrs={'class': 'filling'}).attrs.get("style")

        if style and (width := style.split(':', 1)) and len(width):
            return float(width[-1].strip('%')) / 100 if width[-1] else None


class DigitalNomadGuideTabScrapper(KeyValueTabScrapper):
    """Class that knows how to scrap the data from the Digital Nomad Guide tab."""

    def __init__(self, soup, **kwargs):
        super().__init__(soup, **kwargs)
        self._tab = self._tab_scroller.find("div", class_="tab tab-digital-nomad-guide")

    def _get_value(self, value_column):
        url = a.attrs.get('href') if (a := value_column.find('a')) else None
        return value_column.text, None, url

    def get_continent(self):
        """Given the city details soup, knows how to take the rank number."""
        return self._tab.find("table", class_="details").find("td", class_="value").get_text()


class CostOfLivingTabScrapper(KeyValueTabScrapper):
    """Class that knows how to scrap the data from the Cost of Living tab."""

    def __init__(self, soup, **kwargs):
        super().__init__(soup, **kwargs)
        self._tab = self._tab_scroller.find("div", class_="tab editable tab-cost-of-living double-width")

    def _get_value(self, value_column):
        # The variable "a" is assigned in the if statement
        url = a.attrs.get('href') if (a := value_column.find('a')) else None
        return value_column.text, None, url


class ProsAndConsTabScrapper(TabScrapper):
    """Class that knows how to scrap the data from the Pros and Cons tab."""

    def __init__(self, soup, **kwargs):
        super().__init__(soup, **kwargs)
        self._tab = self._tab_scroller.find("div", class_="tab tab-pros-cons")
        self._keys_dict = {0: 'pros', 1: 'cons'}

    def _get_information(self):
        """
        Iterates over both divs pros and cons, builds an array with all the pros and all the cons, and returns a dict
        with the type {pros: [...pros], cons: [...cons]}.
        """
        pros_cons = []
        pros_cons_dict = {}

        for i, div in enumerate(self._tab.find_all("div")):
            for p in div.find_all("p"):
                pro_con = p.get_text(strip=True)
                pros_cons.append(pro_con)
            pros_cons_dict.update({self._keys_dict[i]: pros_cons})
            pros_cons = []

        return pros_cons_dict


class ReviewsTabScrapper(TabScrapper):
    """Class that knows how to scrap the data from the Reviews tab."""

    def __init__(self, soup, **kwargs):
        super().__init__(soup, **kwargs)
        self._tab = self._tab_scroller.find("div", class_="tab tab-reviews")

    def _get_review(self, element):
        return element.find("div", class_="review-text").text

    def _get_published_date(self, element):
        return element.find("meta", attrs={'itemprop': 'datePublished'}).attrs.get('content')

    def _get_information(self):
        """Takes all the reviews in the tab, and returns an array with all of them."""
        reviews = self._tab.find_all("div", class_="review", attrs={'itemprop': 'review'})
        return [(self._get_review(elem), self._get_published_date(elem)) for elem in reviews]


class WeatherTabScrapper(TabScrapper):
    """Class that knows how to scrap the data from the Weather tab."""

    def __init__(self, soup, **kwargs):
        super().__init__(soup, **kwargs)
        self._tab = self._tab_scroller.find("div", class_="tab tab-weather")
        self.climate_table = self._tab.find("table", class_="climate")
        self._value_getters_by_key = {**dict.fromkeys(['Feels', 'Real'], self._get_temperature),
                                      **dict.fromkeys(['Humidity', 'Rain', 'Cloud', 'Air quality', 'Sun'],
                                                      self._get_weather_indexes)}

    def _get_information(self):
        """Takes all the value from the weather matrix, and builds a dict with tuples for each weather attribute.
        Then, returns the dict."""
        weather_dict = {}
        table_body = self.climate_table

        rows = table_body.find_all('tr')
        months = [col.get_text() for col in rows[0].find_all('td')[1:]]

        for row in rows[1:]:
            cols = row.find_all('td')
            key = cols[0].get_text()
            value_getter = self._value_getters_by_key.get(key, self._get_remote_workers)

            weather_dict.update({key: [(months[i],) + value_getter(col) for i, col in enumerate(cols[1:])]})

        return weather_dict

    def _get_temperature(self, col):
        metric, desc = col.find("span", class_="metric"), col.find("span", class_="")
        return tuple([value.get_text(strip=True) for value in [metric, desc]])

    def _get_weather_indexes(self, col):
        if contents := col.span.contents:
            return contents[2] if len(contents) > 2 else None, contents[0]
        return None, None

    def _get_remote_workers(self, col):
        return col.span.get_text(strip=False), None


class PhotosTabScrapper(TabScrapper):
    """Class that knows how to scrap data from the Photos tab."""

    def __init__(self, soup, **kwargs):
        super().__init__(soup, **kwargs)
        self._tab = self._tab_scroller.find("div", class_="tab tab-photos")

    def _get_information(self):
        """Takes all the pictures from the tab, and returns an array with all of them."""
        return [photo.attrs["data-src"] for photo in self._tab.find_all("img", class_="lazyload")]


class CityGridTabScrapper(TabScrapper):
    """Class that knows how to handle tabs with a grid of cities.."""

    def _get_text(self, city):
        return city.find("div", class_="text").h3.a.text.replace(LATIN1_NON_BREAKING_SPACE, u' ')

    def _get_information(self):
        """Takes all the names of the cities in the grid. Returns an array with all the names."""
        grid = self._tab.find("div", class_="details grid show")
        cities = grid.find_all("li", attrs={'data-type': 'city'})
        return [self._get_text(city) for city in cities]


class NearTabScrapper(CityGridTabScrapper):
    """Class that knows how to scrap data from the Near tab."""

    def __init__(self, soup, **kwargs):
        super().__init__(soup, **kwargs)
        self._tab = self._tab_scroller.find("div", class_="tab tab-near")


class NextTabScrapper(CityGridTabScrapper):
    """Class that knows how to scrap data from the Next tab."""

    def __init__(self, soup, **kwargs):
        super().__init__(soup, **kwargs)
        self._tab = self._tab_scroller.find("div", class_="tab tab-next")


class SimilarTabScrapper(CityGridTabScrapper):
    """Class that knows how to scrap data from the Similar tab."""

    def __init__(self, soup, **kwargs):
        super().__init__(soup, **kwargs)
        self._tab = self._tab_scroller.find("div", class_="tab tab-similar")


def main():
    nomadlist_lisbon_url = "https://nomadlist.com/lisbon"
    nomadlist_lisbon_text = rq.get(nomadlist_lisbon_url).content
    nomadlist_lisbon_soup = BeautifulSoup(nomadlist_lisbon_text, "html.parser")

    scores_tab_scrapper = ScoresTabScrapper(nomadlist_lisbon_soup)
    print(scores_tab_scrapper.get_information())

    digital_nomad_guide_tab_scrapper = DigitalNomadGuideTabScrapper(nomadlist_lisbon_soup)
    print(digital_nomad_guide_tab_scrapper.get_information())

    cost_of_living_tab_scrapper = CostOfLivingTabScrapper(nomadlist_lisbon_soup)
    print(cost_of_living_tab_scrapper.get_information())

    pros_and_cons_tab_scrapper = ProsAndConsTabScrapper(nomadlist_lisbon_soup)
    print(pros_and_cons_tab_scrapper.get_information())

    reviews_tab_scrapper = ReviewsTabScrapper(nomadlist_lisbon_soup)
    print(reviews_tab_scrapper.get_information())

    weather_tab_scrapper = WeatherTabScrapper(nomadlist_lisbon_soup)
    print(weather_tab_scrapper.get_information())

    photos_tab_scrapper = PhotosTabScrapper(nomadlist_lisbon_soup)
    print(photos_tab_scrapper.get_information())

    near_tab_scrapper = NearTabScrapper(nomadlist_lisbon_soup)
    print(near_tab_scrapper.get_information())

    next_tab_scrapper = NextTabScrapper(nomadlist_lisbon_soup)
    print(next_tab_scrapper.get_information())

    similar_tab_scrapper = SimilarTabScrapper(nomadlist_lisbon_soup)
    print(similar_tab_scrapper.get_information())

    print("Lets got to sleep before starting again...")
    time.sleep(5)


if __name__ == "__main__":
    main()
