from scrapper.nomad_list_scrapper import NomadListScrapper


def main():
    cities = NomadListScrapper().get_cities()
    print("Cities:")
    print(cities)


if __name__ == "__main__":
    main()
