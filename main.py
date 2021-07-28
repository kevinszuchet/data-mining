import json
import sys

from scrapper.nomad_list_scrapper import NomadListScrapper
from conf import JSON_FILENAME, NOMAD_LIST_URL
from logger import Logger
from scrapper.web_driver import WebDriver


def main():
    logger = Logger().logger
    web_driver = WebDriver(logger, NOMAD_LIST_URL)
    try:
        cities = NomadListScrapper(logger, web_driver).get_cities()
        logger.info(f"Finished Scrapping Cities")
    except Exception as e:
        # exc_info=True to log the traceback
        logger.error(f"Exception raised: {e}")
        sys.exit(1)
    with open(JSON_FILENAME, "w+") as opened_file:
        json.dump(cities, opened_file, indent=2)
    logger.info(f'Successfully saved {JSON_FILENAME}')


if __name__ == "__main__":
    main()
