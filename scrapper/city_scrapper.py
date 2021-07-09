import re
from bs4 import BeautifulSoup
from scrapper.attribute_element_scrapper import AttributeElementScrapper


class CityScrapper:
    """Class that knows how to get data from each city card."""
    action_regex = re.compile(r'(label|rating)-(\w+)-score')

    @staticmethod
    def get_city_url(city_li):
        """Given the city li, returns the url of it to go to the details."""
        text = city_li.find(class_="text")
        return text.h2.a.attrs["href"].strip()

    def get_city_details(self, city_details_html):
        """
        Given the city details html, takes all the available information about the city within the tabs.
        Then, returns a dict with all that information.
        """

        soup = BeautifulSoup(city_details_html, "html.parser")
        # TODO iterate over all the tabs scrappers to get all the available information about the city
        # return {tab_scrapper.tab_name(): tab_scrapper.get_information() for tab_scrapper in list_of_tabs_scrappers}
        return city_details_html

    def OLD_get_city_details(self, city_li):
        """
        Given the city li, takes all the available information about the city.
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

                # TODO Avoid mutability

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
        attribute = {}
        for span in city_li.find(class_="attributes").find_all("span", class_="element"):
            position = span['class'][1]
            attribute_element_scrapper = AttributeElementScrapper(position)
            attribute.update(attribute_element_scrapper.get_info(span))
        return attributes
