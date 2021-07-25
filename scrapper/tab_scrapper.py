import time

from bs4 import BeautifulSoup
import requests as rq
from logger import Logger

LATIN1_NON_BREAKING_SPACE = u'\xa0'


class TabScrapper:
    def __init__(self, soup, logger=None):
        container = soup.find("div", class_="tab-scroller-container")
        self._tab_scroller = container.find("div", class_="tab-scroller")
        if logger is None:
            logger = Logger().logger
        self._logger = logger

    @staticmethod
    def get_name(tab):
        return tab.find("a").get_text(strip=True).replace(' ', '')

    @staticmethod
    def is_valid(tab):
        try:
            dynamic_tab_scrapper = eval(f"{TabScrapper.get_name(tab)}TabScrapper")
        except NameError:
            return False
        else:
            return issubclass(dynamic_tab_scrapper, TabScrapper)

    def get_information(self):
        pass


class KeyValueTabScrapper(TabScrapper):
    def _get_key(self, key_column):
        return key_column.get_text(strip=True)

    def _get_value(self, value_column):
        return value_column.text

    def get_information(self):
        info_dict = {}
        table = self._tab.find('table', class_='details')
        for row in table.find_all('tr'):
            row_key, row_value = row.find(class_='key'), row.find(class_='value')
            key, value = self._get_key(row_key), self._get_value(row_value)
            info_dict.update({key: value})

        return info_dict


class ScoresTabScrapper(KeyValueTabScrapper):
    def __init__(self, soup, **kwargs):
        super().__init__(soup, **kwargs)
        self._tab = self._tab_scroller.find("div", class_="tab tab-ranking show")

    def _get_value(self, value_column):
        # TODO get Rating Value, Best Rating, and Width
        return value_column.div.div.text


class DigitalNomadGuideTabScrapper(KeyValueTabScrapper):
    def __init__(self, soup, **kwargs):
        super().__init__(soup, **kwargs)
        self._tab = self._tab_scroller.find("div", class_="tab tab-digital-nomad-guide")


class CostOfLivingTabScrapper(KeyValueTabScrapper):
    def __init__(self, soup, **kwargs):
        super().__init__(soup, **kwargs)
        self._tab = self._tab_scroller.find("div", class_="tab editable tab-cost-of-living double-width")


class ProsAndConsTabScrapper(TabScrapper):
    def __init__(self, soup, **kwargs):
        super().__init__(soup, **kwargs)
        self._tab = self._tab_scroller.find("div", class_="tab tab-pros-cons")
        self._keys_dict = {0: 'pros', 1: 'cons'}

    def get_information(self):
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
    def __init__(self, soup, **kwargs):
        super().__init__(soup, **kwargs)
        self._tab = self._tab_scroller.find("div", class_="tab tab-reviews")

    def get_information(self):
        return [review_element.text for review_element in self._tab.find_all("div", class_="review-text")]


class WeatherTabScrapper(TabScrapper):
    def __init__(self, soup, **kwargs):
        super().__init__(soup, **kwargs)
        self._tab = self._tab_scroller.find("div", class_="tab tab-weather")
        self.climate_table = self._tab.find("table", class_="climate")

    def get_information(self):
        weather_dict = {}
        table_body = self.climate_table

        rows = table_body.find_all('tr')
        months = [col.get_text() for col in rows[0].find_all('td')[1:]]
        for row in rows[1:]:
            cols = row.find_all('td')
            key = cols[0].get_text()
            # TODO Get rid of empty values
            # TODO Contemplate percents, imperial, metric and other units (now the value is all the text together)
            weather_dict.update({key: [(months[i], col.get_text(strip=True)) for i, col in enumerate(cols[1:])]})

        return weather_dict


class PhotosTabScrapper(TabScrapper):
    def __init__(self, soup, **kwargs):
        super().__init__(soup, **kwargs)
        self._tab = self._tab_scroller.find("div", class_="tab tab-photos")

    def get_information(self):
        return [photo.attrs["data-src"] for photo in self._tab.find_all("img", class_="lazyload")]


class CityGridTabScrapper(TabScrapper):
    def _get_text(self, city):
        return city.find("div", class_="text").h3.a.text.replace(LATIN1_NON_BREAKING_SPACE, u' ')

    def get_information(self):
        grid = self._tab.find("div", class_="details grid show")
        cities = grid.find_all("li", attrs={'data-type': 'city'})
        return [self._get_text(city) for city in cities]


class NearTabScrapper(CityGridTabScrapper):
    def __init__(self, soup, **kwargs):
        super().__init__(soup, **kwargs)
        self._tab = self._tab_scroller.find("div", class_="tab tab-near")


class NextTabScrapper(CityGridTabScrapper):
    def __init__(self, soup, **kwargs):
        super().__init__(soup, **kwargs)
        self._tab = self._tab_scroller.find("div", class_="tab tab-next")


class SimilarTabScrapper(CityGridTabScrapper):
    def __init__(self, soup, **kwargs):
        super().__init__(soup, **kwargs)
        self._tab = self._tab_scroller.find("div", class_="tab tab-similar")


def main():
    nomadlist_lisbon_url = "https://nomadlist.com/lisbon"
    nomadlist_lisbon_text = rq.get(nomadlist_lisbon_url).content
    nomadlist_lisbon_soup = BeautifulSoup(nomadlist_lisbon_text, "html.parser")

    tab_scrapper_soup_object = TabScrapper(nomadlist_lisbon_soup)
    tab_scrapper_tabs_dict = tab_scrapper_soup_object.get_information()
    print(tab_scrapper_tabs_dict)

    scores_tab_scrapper_object = ScoresTabScrapper(nomadlist_lisbon_soup)
    print(scores_tab_scrapper_object.get_information())

    digital_nomad_guide_tab_scrapper_object = DigitalNomadGuideTabScrapper(nomadlist_lisbon_soup)
    print(digital_nomad_guide_tab_scrapper_object.get_information())

    cost_of_living_tab_scrapper_object = CostOfLivingTabScrapper(nomadlist_lisbon_soup)
    print(cost_of_living_tab_scrapper_object.get_information())

    pros_and_cons_tab_scrapper_object = ProsAndConsTabScrapper(nomadlist_lisbon_soup)
    print(pros_and_cons_tab_scrapper_object.get_information())

    reviews_tab_scrapper_object = ReviewsTabScrapper(nomadlist_lisbon_soup)
    print(reviews_tab_scrapper_object.get_information())

    weather_tab_scrapper_object = WeatherTabScrapper(nomadlist_lisbon_soup)
    print(weather_tab_scrapper_object.get_information())

    photos_tab_scrapper_object = PhotosTabScrapper(nomadlist_lisbon_soup)
    print(photos_tab_scrapper_object.get_information())

    near_tab_scrapper_object = NearTabScrapper(nomadlist_lisbon_soup)
    print(near_tab_scrapper_object.get_information())

    next_tab_scrapper_object = NextTabScrapper(nomadlist_lisbon_soup)
    print(next_tab_scrapper_object.get_information())

    similar_tab_scrapper_object = SimilarTabScrapper(nomadlist_lisbon_soup)
    print(similar_tab_scrapper_object.get_information())

    time.sleep(5)


if __name__ == "__main__":
    main()
