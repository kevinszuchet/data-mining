import json
from scrapper.nomad_list_scrapper import NomadListScrapper
from conf import JSON_FILENAME


def main():
    cities = NomadListScrapper().get_cities()
    with open(JSON_FILENAME, "w+") as opened_file:
        json.dump(cities, opened_file, indent=2)
    print("Cities:", cities)


if __name__ == "__main__":
    main()
