from bs4 import BeautifulSoup
import requests as rq


class TabScrapper:
    def __init__(self, soup_object):
        self.soup_object = soup_object
        self.div_tabs = self.soup_object.find("div", class_="tabs").find("div", class_="ul")
        # print(f'ul: {self.ul.prettify()}')

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
        for tab_element in self.ul.find_all("h2", class_="li active"):
            tab_title_element = tab_element.find("a")  # , title="Lisbon City Scores"
            tab_title = tab_title_element.get_text(strip=True)
            tab_link = tab_title_element["href"]

            tabs_dict[tab_title] = tab_link

        for tab_element in self.ul.find_all("h2", class_="li"):
            tab_title_element = tab_element.find("a").get_text(strip=True)
            tab_title = tab_title_element.get_text(strip=True)
            tab_link = tab_title_element["href"]

            tabs_dict[tab_title] = tab_link

        return tabs_dict


class ScoresTabScrapper(TabScrapper):
    def __init__(self, soup_object):
        super().__init__(soup_object)
        # self.tabs_dict = tabs_dict
        # self.scores_tab_path = "https://nomadlist.com" + self.tabs_dict['Scores']
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
        # self.tabs_dict = tabs_dict
        # self.scores_tab_path = "https://nomadlist.com" + self.tabs_dict['Digital Nomad Guide']
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
        # self.tabs_dict = tabs_dict
        # self.scores_tab_path = "https://nomadlist.com" + self.tabs_dict['Cost of Living']
        self.div_tabs_scroll_cont = self.soup_object.find("div", class_="tab-scroller-container")
        self.tab_scroller = self.div_tabs_scroll_cont.find("div", class_="tab-scroller")
        self.tab_cost_of_living = self.tab_scroller.find("div", class_="tab editable tab-cost-of-living double-width")
        # print(f'tab-cost-of-living: {self.tab_cost_of_living.prettify()}')

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
        # self.tabs_dict = tabs_dict
        # self.scores_tab_path = "https://nomadlist.com" + self.tabs_dict['Cost of Living']
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
        # self.tabs_dict = tabs_dict
        # self.scores_tab_path = "https://nomadlist.com" + self.tabs_dict['Cost of Living']
        self.div_tabs_scroll_cont = self.soup_object.find("div", class_="tab-scroller-container")
        self.tab_scroller = self.div_tabs_scroll_cont.find("div", class_="tab-scroller")
        self.tab_reviews = self.tab_scroller.find("div", class_="tab tab-reviews")

    def get_information(self):
        list_of_reviews = []
        list_of_pros_list_and_cons_list = []
        for review_element in self.tab_reviews.find_all("div", class_="review-text"):
            review_text = review_element.text
            list_of_reviews.append(review_text)

        return list_of_reviews


class WeatherTabScrapper(TabScrapper):
    def __init__(self, soup_object):
        super().__init__(soup_object)
        # self.tabs_dict = tabs_dict
        # self.scores_tab_path = "https://nomadlist.com" + self.tabs_dict['Cost of Living']
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


# TODO RemoteJobs?, Reviews?, Photos?
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


if __name__ == "__main__":
    main()
