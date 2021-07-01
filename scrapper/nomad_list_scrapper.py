import re
import requests
from bs4 import BeautifulSoup
from conf import NOMAD_LIST_URL


class NomadListScrapper:
    """Class responsible to handle the scrapper in the Nomad List site."""

    action_regex = re.compile(r'(label|rating)-(\w+)-score')

    def __init__(self):
        self._baseUrl = NOMAD_LIST_URL

    def get_cities(self):
        """
        Takes the cities from the home page, builds a dictionary for each one with the available information.
        Then, returns a list of dicts with all the cities.
        """
        home_page = self.get_home_page()
        soup = BeautifulSoup(home_page, "html.parser")

        return [self.get_city_information(city_li) for city_li in soup.find_all(attrs={'data-type': 'city'})]

        return cities

    def get_home_page(self):
        """Tries to get the content of the home page."""
        response = requests.get(self._baseUrl)

        if response.status_code == requests.codes.ok:
            return response.content

        # TODO show nice error messages
        response.raise_for_status()

    def get_city_information(self, city_li):
        """
        Given the city li, takes all the information available in the home page.
        Then, returns a dict with all that information.
        """
        text = city_li.find(class_="text")

        city = {
            'city': text.h2.text if text.h2 else "-",
            'country': text.h3.text if text.h3 else "-",
            'description': city_li.find(class_="action").p.text,
            'actions': self.get_city_actions(city_li),
            'attributes': self.get_city_attributes(city_li)
        }

        return city

    def get_city_actions(self, city_li):
        """
        Given the city li, takes all the information about the actions in the city card.
        Returns all the actions as a list of dicts.
        """
        actions = []
        action = {}
        for action_span in city_li.find(class_="action").find_all("span"):
            score_class_name = action_span['class'][0]
            match = self.action_regex.match(score_class_name)
            if match:
                span_type = match.group(1)
                action_name = match.group(2)

                if span_type == "label":
                    # TODO review where the 'All' (next to Overall) come from and replace it by nothing!
                    label = action_span.text.replace("All", "").strip() if action_span.text else '-'
                    action.update({'label': label})
                elif span_type == "rating":
                    rating_percent = action_span.span.attrs["style"].replace("width:", "").replace("%", "")
                    rating_percent = float(rating_percent) if rating_percent.isnumeric() else '-'
                    action.update({'rating': action_span.text.strip() or '-', 'rating_percent': rating_percent})
                    actions.append(action)
                    action = {}

        return actions

    def get_city_attributes(self, city_li):
        """
        Given the city li, takes all the information about the attributes in the city card.
        Returns all the attributes as a list of dicts.
        """
        attributes = []
        for attribute_element_span in city_li.find(class_="attributes").find_all("span", class_="element"):
            attribute = {}
            position = attribute_element_span['class'][1]
            if position == "bottom-left":
                weather_emoji = attribute_element_span.find("span", class_="weather-emoji").text
                temperature = attribute_element_span.find("span", class_="temperature")
                attribute.update({'temperature': {}, 'heat_index': {}})
                for heat_index_span in temperature.find("span", class_="label-heat-index").find_all("span",
                                                                                                    class_="value"):
                    attribute['heat_index'].update({heat_index_span['class'][-1]: heat_index_span.text})
                for temperature_span in temperature.find_all("span", class_="value"):
                    # TODO review. It takes all the span.value (find siblings)
                    attribute['temperature'].update({temperature_span['class'][-1]: temperature_span.text})
                air_quality = attribute_element_span.find("span", class_="air_quality")
                attribute.update(
                    {air_quality.find("span", class_="above").text: air_quality.find("span", class_="value").text})
            elif position == "top-left":
                # TODO complete this
                pass
            elif position == "bottom-right":
                attribute.update({'price': attribute_element_span.span.text})
            elif position == "top-right":
                internet_span = attribute_element_span.find("span", class_="right")
                print("internet_span", internet_span)
                attribute.update({'internet': {'value': internet_span.find("span", class_="value").text,
                                               'unit': internet_span.find("span", class_="mbps").text}})
        return attributes
