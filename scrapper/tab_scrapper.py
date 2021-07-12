from .city_scrapper import CityScrapper


class TabScrapper:
    def get_information(self):
        city_info = CityScrapper.get_city_details()

        pass


class KeyValueTabScrapper(TabScrapper):
    def get_information(self):
        pass


class ScoreTabScrapper(KeyValueTabScrapper):
    def get_information(self):
        pass


class DigitalNomadGuideTabScrapper(KeyValueTabScrapper):
    def get_information(self):
        pass


class CostOfLivingTabScrapper(KeyValueTabScrapper):
    def get_information(self):
        pass


class ProsAndCons(TabScrapper):
    def get_information(self):
        pass


print(CityScrapper)
# TODO RemoteJobs?, Reviews?, Photos?
