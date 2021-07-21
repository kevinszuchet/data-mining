from bs4 import BeautifulSoup
import requests as rq
import re
from logger import Logger


class TabScrapper:
    def __init__(self, soup_object):
        self.soup_object = soup_object
        self.div_tabs = self.soup_object.find("div", class_="tabs").find("div", class_="ul")
        self._logger = Logger().logger

    @staticmethod
    def tab_name(tab):
        return tab.find("a").get_text(strip=True).replace(' ', '')

    @staticmethod
    def valid_tab(tab):
        try:
            eval(f"{TabScrapper.tab_name(tab)}TabScrapper")
        except NameError:
            return False
        else:
            return True

    def get_information(self):
        tabs_dict = {}

        for tab_element in self.div_tabs.find_all("h2", class_="li active"):
            tab_title_element = tab_element.find("a")
            tab_title = tab_title_element.get_text(strip=True)
            tab_link = tab_title_element["href"]

            tabs_dict[tab_title] = tab_link

        for tab_element in self.div_tabs.find_all("h2", class_="li"):
            tab_title_element = tab_element.find("a")
            tab_title = tab_title_element.get_text(strip=True)
            tab_link = tab_title_element["href"]

            tabs_dict[tab_title] = tab_link

        return tabs_dict


class ScoresTabScrapper(TabScrapper):
    def __init__(self, soup_object):
        super().__init__(soup_object)
        self.div_tabs_scroll_cont = self.soup_object.find("div", class_="tab-scroller-container")
        self.tab_scroller = self.div_tabs_scroll_cont.find("div", class_="tab-scroller")
        self.tab_ranking = self.tab_scroller.find("div", class_="tab tab-ranking show")

    def get_information(self):
        list_of_keys = []
        list_of_values = []

        for key_element in self.tab_ranking.find_all("td", class_="key"):
            score_title = key_element.get_text(strip=True)
            list_of_keys.append(score_title)

        for value_element in self.tab_ranking.find_all("td", class_="value"):
            score_value = value_element.div.div.text
            list_of_values.append(score_value)

        scores_tab_info_dict = dict(zip(list_of_keys, list_of_values))

        return scores_tab_info_dict


class DigitalNomadGuideTabScrapper(TabScrapper):
    def __init__(self, soup_object):
        super().__init__(soup_object)
        self.div_tabs_scroll_cont = self.soup_object.find("div", class_="tab-scroller-container")
        self.tab_scroller = self.div_tabs_scroll_cont.find("div", class_="tab-scroller")
        self.tab_digital_nomad_guide = self.tab_scroller.find("div", class_="tab tab-digital-nomad-guide")

    def get_information(self):
        list_of_keys = []
        list_of_values = []

        for key_element in self.tab_digital_nomad_guide.find_all("td", class_="key"):
            score_title = key_element.get_text(strip=True)
            list_of_keys.append(score_title)

        for value_element in self.tab_digital_nomad_guide.find_all("td", class_="value"):
            score_value = value_element.text
            list_of_values.append(score_value)

        scores_tab_info_dict = dict(zip(list_of_keys, list_of_values))

        return scores_tab_info_dict


class CostOfLivingTabScrapper(TabScrapper):
    def __init__(self, soup_object):
        super().__init__(soup_object)
        self.div_tabs_scroll_cont = self.soup_object.find("div", class_="tab-scroller-container")
        self.tab_scroller = self.div_tabs_scroll_cont.find("div", class_="tab-scroller")
        self.tab_cost_of_living = self.tab_scroller.find("div", class_="tab editable tab-cost-of-living double-width")

    def get_information(self):
        list_of_keys = []
        list_of_values = []

        for key_element in self.tab_cost_of_living.find_all("td", class_="key"):
            cost_of_living_title = key_element.get_text(strip=True)
            list_of_keys.append(cost_of_living_title)

        for value_element in self.tab_cost_of_living.find_all("td", class_="value"):
            cost_of_living_value = value_element.text
            list_of_values.append(cost_of_living_value)

        scores_tab_info_dict = dict(zip(list_of_keys, list_of_values))

        return scores_tab_info_dict


class ProsAndConsTabScrapper(TabScrapper):
    def __init__(self, soup_object):
        super().__init__(soup_object)
        self.div_tabs_scroll_cont = self.soup_object.find("div", class_="tab-scroller-container")
        self.tab_scroller = self.div_tabs_scroll_cont.find("div", class_="tab-scroller")
        self.tab_pros_cons = self.tab_scroller.find("div", class_="tab tab-pros-cons")

    def get_information(self):
        list_of_pros_cons = []
        list_of_pros_list_and_cons_list = []

        for p_element in self.tab_pros_cons.find_all("div"):
            for pros_cons_element in p_element.find_all("p"):
                pros_cons = pros_cons_element.get_text(strip=True)
                list_of_pros_cons.append(pros_cons)
            list_of_pros_list_and_cons_list.append(list_of_pros_cons)
            list_of_pros_cons = []

        return list_of_pros_list_and_cons_list


class ReviewsTabScrapper(TabScrapper):
    def __init__(self, soup_object):
        super().__init__(soup_object)
        self.div_tabs_scroll_cont = self.soup_object.find("div", class_="tab-scroller-container")
        self.tab_scroller = self.div_tabs_scroll_cont.find("div", class_="tab-scroller")
        self.tab_reviews = self.tab_scroller.find("div", class_="tab tab-reviews")

    def get_information(self):
        list_of_reviews = []

        for review_element in self.tab_reviews.find_all("div", class_="review-text"):
            review_text = review_element.text
            list_of_reviews.append(review_text)

        return list_of_reviews


class WeatherTabScrapper(TabScrapper):
    def __init__(self, soup_object):
        super().__init__(soup_object)
        self.div_tabs_scroll_cont = self.soup_object.find("div", class_="tab-scroller-container")
        self.tab_scroller = self.div_tabs_scroll_cont.find("div", class_="tab-scroller")
        self.tab_weather = self.tab_scroller.find("div", class_="tab tab-weather")
        self.climate_table = self.tab_weather.find("table", class_="climate")

    def get_information(self):
        weather_data = []
        table_body = self.climate_table

        rows = table_body.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            cols = [ele.text.strip() for ele in cols]
            weather_data.append([ele for ele in cols if ele])  # Get rid of empty values

        return weather_data


class PhotosTabScrapper(TabScrapper):
    def __init__(self, soup_object):
        super().__init__(soup_object)
        self.div_tabs_scroll_cont = self.soup_object.find("div", class_="tab-scroller-container")
        self.tab_scroller = self.div_tabs_scroll_cont.find("div", class_="tab-scroller")
        self.tab_photos = self.tab_scroller.find("div", class_="tab tab-photos")

    def get_information(self):
        list_of_photos = []
        for photo_element in self.tab_photos.find_all("div", class_="photo-column"):
            for photo_url_element in photo_element.find_all("img", class_="lazyload"):
                photos_urls = photo_url_element.attrs["data-src"]
                list_of_photos.append(photos_urls)

        return list_of_photos


class NearTabScrapper(TabScrapper):
    def __init__(self, soup_object):
        super().__init__(soup_object)
        self.div_tabs_scroll_cont = self.soup_object.find("div", class_="tab-scroller-container")
        self.tab_scroller = self.div_tabs_scroll_cont.find("div", class_="tab-scroller")
        self.tab_near = self.tab_scroller.find("div", class_="tab tab-near")

    def get_information(self):
        info_of_nearby_cities = {}

        for near_element in self.tab_near.find("div", class_="details grid show"):    # find_all("li data-type=city")
            city = near_element.find("div", class_="text").h3.a.text

            country = near_element.find("div", class_="text").h4.a.text

            description = near_element.find("p", class_="description").text

            overall_title = near_element.find("span", class_="label-main-score label").text
            overall_style_extract = near_element.find("span", class_=re.compile("rating-main-score rating "))\
                .find('span', attrs={'class': 'filling'})
            overall_style_extract2 = overall_style_extract["style"]
            overall_style = overall_style_extract2.split(':', 1)[-1]
            overall = (overall_title, overall_style)

            cost_title = near_element.find("span", class_="label-cost-score label").text.rstrip("\xa0")
            cost_style_extract = near_element.find("span", class_=re.compile("rating-cost-score rating "))\
                .find('span', attrs={'class': 'filling'})
            cost_style_extract2 = cost_style_extract["style"]
            cost_style = cost_style_extract2.split(':', 1)[-1]
            cost = (cost_title, cost_style)

            internet_title = near_element.find("span", class_="label-internet-score label").text.rstrip("\xa0")
            internet_style_extract = near_element.find("span", class_=re.compile("rating-internet-score rating "))\
                .find('span', attrs={'class': 'filling'})
            internet_style_extract2 = internet_style_extract["style"]
            internet_style = internet_style_extract2.split(':', 1)[-1]
            internet = (internet_title, internet_style)

            fun_title = near_element.find("span", class_="label-fun-score label").text.rstrip("\xa0")
            fun_style_extract = near_element.find("span", class_=re.compile("rating-fun-score rating "))\
                .find('span', attrs={'class': 'filling'})
            fun_style_extract2 = fun_style_extract["style"]
            fun_style = fun_style_extract2.split(':', 1)[-1]
            fun = (fun_title, fun_style)

            safety_title = near_element.find("span", class_="label-safety-score label").text.rstrip("\xa0")
            safety_style_extract = near_element.find("span", class_=re.compile("rating-safety-score rating "))\
                .find('span', attrs={'class': 'filling'})
            safety_style_extract2 = safety_style_extract["style"]
            safety_style = safety_style_extract2.split(':', 1)[-1]
            safety = (safety_title, safety_style)

            weather_emoji = near_element.find("span", class_="weather-emoji").text
            temperature = near_element.find("span", class_=re.compile("temperature"))\
                .find('span', class_="value unit metric").text
            weather = f'{weather_emoji} {temperature}C'

            air_quality = near_element.find("span", class_="air_quality").text

            travel_distance = near_element.find("span", class_="element top-left").text

            price = near_element.find("span", class_="element bottom-right short_term_cost cost switchable").text

            list_of_info_for_each_city = [country, description, overall, cost, internet, fun, safety, weather,
                                          air_quality, travel_distance, price]

            info_of_nearby_cities[city] = list_of_info_for_each_city

        return info_of_nearby_cities


class NextTabScrapper(TabScrapper):
    def __init__(self, soup_object):
        super().__init__(soup_object)
        self.div_tabs_scroll_cont = self.soup_object.find("div", class_="tab-scroller-container")
        self.tab_scroller = self.div_tabs_scroll_cont.find("div", class_="tab-scroller")
        self.tab_next = self.tab_scroller.find("div", class_="tab tab-next")

    def get_information(self):
        info_of_nearby_cities = {}

        for near_element in self.tab_next.find("div", class_="details grid show"):    # find_all("li data-type=city")
            city = near_element.find("div", class_="text").h3.a.text

            country = near_element.find("div", class_="text").h4.a.text

            description = near_element.find("p", class_="description").text

            overall_title = near_element.find("span", class_="label-main-score label").text
            overall_style_extract = near_element.find("span", class_=re.compile("rating-main-score rating "))\
                .find('span', attrs={'class': 'filling'})
            overall_style_extract2 = overall_style_extract["style"]
            overall_style = overall_style_extract2.split(':', 1)[-1]
            overall = (overall_title, overall_style)

            cost_title = near_element.find("span", class_="label-cost-score label").text.rstrip("\xa0")
            cost_style_extract = near_element.find("span", class_=re.compile("rating-cost-score rating "))\
                .find('span', attrs={'class': 'filling'})
            cost_style_extract2 = cost_style_extract["style"]
            cost_style = cost_style_extract2.split(':', 1)[-1]
            cost = (cost_title, cost_style)

            internet_title = near_element.find("span", class_="label-internet-score label").text.rstrip("\xa0")
            internet_style_extract = near_element.find("span", class_=re.compile("rating-internet-score rating "))\
                .find('span', attrs={'class': 'filling'})
            internet_style_extract2 = internet_style_extract["style"]
            internet_style = internet_style_extract2.split(':', 1)[-1]
            internet = (internet_title, internet_style)

            fun_title = near_element.find("span", class_="label-fun-score label").text.rstrip("\xa0")
            fun_style_extract = near_element.find("span", class_=re.compile("rating-fun-score rating "))\
                .find('span', attrs={'class': 'filling'})
            fun_style_extract2 = fun_style_extract["style"]
            fun_style = fun_style_extract2.split(':', 1)[-1]
            fun = (fun_title, fun_style)

            safety_title = near_element.find("span", class_="label-safety-score label").text.rstrip("\xa0")
            safety_style_extract = near_element.find("span", class_=re.compile("rating-safety-score rating "))\
                .find('span', attrs={'class': 'filling'})
            safety_style_extract2 = safety_style_extract["style"]
            safety_style = safety_style_extract2.split(':', 1)[-1]
            safety = (safety_title, safety_style)

            weather_emoji = near_element.find("span", class_="weather-emoji").text
            temperature = near_element.find("span", class_=re.compile("temperature"))\
                .find('span', class_="value unit metric").text
            weather = f'{weather_emoji} {temperature}C'

            air_quality = near_element.find("span", class_="air_quality").text

            travel_distance = near_element.find("span", class_="element top-left").text

            price = near_element.find("span", class_="element bottom-right short_term_cost cost switchable").text

            list_of_info_for_each_city = [country, description, overall, cost, internet, fun, safety, weather,
                                          air_quality, travel_distance, price]

            info_of_nearby_cities[city] = list_of_info_for_each_city

        return info_of_nearby_cities


class SimilarTabScrapper(TabScrapper):
    def __init__(self, soup_object):
        super().__init__(soup_object)
        self.div_tabs_scroll_cont = self.soup_object.find("div", class_="tab-scroller-container")
        self.tab_scroller = self.div_tabs_scroll_cont.find("div", class_="tab-scroller")
        self.tab_similar = self.tab_scroller.find("div", class_="tab tab-similar")

    def get_information(self):
        info_of_nearby_cities = {}

        for near_element in self.tab_similar.find("div", class_="details grid show"):    # find_all("li data-type=city")
            # print(f'near_element : {near_element.prettify()}')
            city = near_element.find("div", class_="text").h3.a.text

            description = near_element.find("p", class_="description").text

            overall_title = near_element.find("span", class_="label-main-score label").text
            overall_style_extract = near_element.find("span", class_=re.compile("rating-main-score rating "))\
                .find('span', attrs={'class': 'filling'})
            overall_style_extract2 = overall_style_extract["style"]
            overall_style = overall_style_extract2.split(':', 1)[-1]
            overall = (overall_title, overall_style)

            cost_title = near_element.find("span", class_="label-cost-score label").text.rstrip("\xa0")
            cost_style_extract = near_element.find("span", class_=re.compile("rating-cost-score rating "))\
                .find('span', attrs={'class': 'filling'})
            cost_style_extract2 = cost_style_extract["style"]
            cost_style = cost_style_extract2.split(':', 1)[-1]
            cost = (cost_title, cost_style)

            internet_title = near_element.find("span", class_="label-internet-score label").text.rstrip("\xa0")
            internet_style_extract = near_element.find("span", class_=re.compile("rating-internet-score rating "))\
                .find('span', attrs={'class': 'filling'})
            internet_style_extract2 = internet_style_extract["style"]
            internet_style = internet_style_extract2.split(':', 1)[-1]
            internet = (internet_title, internet_style)

            fun_title = near_element.find("span", class_="label-fun-score label").text.rstrip("\xa0")
            fun_style_extract = near_element.find("span", class_=re.compile("rating-fun-score rating "))\
                .find('span', attrs={'class': 'filling'})
            fun_style_extract2 = fun_style_extract["style"]
            fun_style = fun_style_extract2.split(':', 1)[-1]
            fun = (fun_title, fun_style)

            safety_title = near_element.find("span", class_="label-safety-score label").text.rstrip("\xa0")
            safety_style_extract = near_element.find("span", class_=re.compile("rating-safety-score rating "))\
                .find('span', attrs={'class': 'filling'})
            safety_style_extract2 = safety_style_extract["style"]
            safety_style = safety_style_extract2.split(':', 1)[-1]
            safety = (safety_title, safety_style)

            weather_emoji = near_element.find("span", class_="weather-emoji").text
            temperature = near_element.find("span", class_=re.compile("temperature"))\
                .find('span', class_="value unit metric").text
            weather = f'{weather_emoji} {temperature}C'

            air_quality = near_element.find("span", class_="air_quality").text

            travel_distance = near_element.find("span", class_="element top-left").text

            price = near_element.find("span", class_="element bottom-right short_term_cost cost switchable").text

            list_of_info_for_each_city = [description, overall, cost, internet, fun, safety, weather,
                                          air_quality, travel_distance, price]

            info_of_nearby_cities[city] = list_of_info_for_each_city

        return info_of_nearby_cities


def main():
    nomadlist_lisbon_url = "https://nomadlist.com/lisbon"
    nomadlist_lisbon_text = rq.get(nomadlist_lisbon_url).text
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


if __name__ == "__main__":
    main()
