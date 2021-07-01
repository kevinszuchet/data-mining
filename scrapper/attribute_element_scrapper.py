class AttributeElementScrapperInterface:
    def get_info(self, span) -> dict:
        """Given the span, takes the information that depends on the element position. Then, returns that info."""
        pass


class BottomLeftAttributeElementScrapper(AttributeElementScrapperInterface):
    def get_info(self, span) -> dict:
        """Given the span, takes the information that depends on the element position. Then, returns that info."""
        attribute = {}
        weather_emoji_span = span.find("span", class_="weather-emoji")
        attribute.update({'weather_emoji': weather_emoji_span.text if weather_emoji_span else '-'})
        temperature = span.find("span", class_="temperature")
        if temperature:
            attribute.update({'temperature': {}, 'heat_index': {}})
            for heat_index_span in temperature.find("span", class_="label-heat-index").find_all("span",
                                                                                                class_="value"):
                attribute['heat_index'].update({heat_index_span['class'][-1]: heat_index_span.text})
            for temperature_span in temperature.find_all("span", class_="value"):
                # TODO review. It takes all the span.value (find siblings)
                attribute['temperature'].update({temperature_span['class'][-1]: temperature_span.text})
        air_quality = span.find("span", class_="air_quality")
        if air_quality:
            attribute.update(
                {air_quality.find("span", class_="above").text: air_quality.find("span", class_="value").text})
        return attribute


class TopLeftAttributeElementScrapper:
    def get_info(self, span) -> dict:
        """Given the span, takes the information that depends on the element position. Then, returns that info."""
        # TODO complete this
        return {}


class BottomRightAttributeElementScrapper:
    def get_info(self, span) -> dict:
        """Given the span, takes the information that depends on the element position. Then, returns that info."""
        if span.span is None:
            return {}

        return {'price': span.span.text}


class TopRightAttributeElementScrapper:
    def get_info(self, span) -> dict:
        """Given the span, takes the information that depends on the element position. Then, returns that info."""
        internet_span = span.find("span", class_="right")
        if internet_span is None:
            return {}

        return {
            'internet': {
                'value': internet_span.find("span", class_="value").text,
                'unit': internet_span.find("span", class_="mbps").text
            }
        }


ATTRIBUTE_ELEMENT_SCRAPPERS = {
    'bottom-left': BottomLeftAttributeElementScrapper,
    'top-left': TopLeftAttributeElementScrapper,
    'bottom-right': BottomRightAttributeElementScrapper,
    'top-right': TopRightAttributeElementScrapper
}


def AttributeElementScrapper(position):
    """Given the position of the element, returns the correct scrapper to get the info."""
    return ATTRIBUTE_ELEMENT_SCRAPPERS[position]()
