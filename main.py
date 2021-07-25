import json
import sys

from scrapper.nomad_list_scrapper import NomadListScrapper
from conf import JSON_FILENAME
from logger import Logger


def main():
    logger = Logger().logger
    try:
        cities = NomadListScrapper(logger).get_cities()
    except Exception as e:
        logger.error(f"Exception raised: {e}")
        sys.exit(1)

    with open(JSON_FILENAME, "w+") as opened_file:
        json.dump(cities, opened_file, indent=2)

    logger.info(f"Cities: {cities}")
    # TODO there is something opened, it doesn't exit the process


if __name__ == "__main__":
    main()
