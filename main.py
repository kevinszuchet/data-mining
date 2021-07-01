from scrapper.nomad_list_scrapper import NomadListScrapper


def main():
    citites = NomadListScrapper().get_cities()
    print("Cities:")
    print(citites)


if __name__ == "__main__":
    main()
