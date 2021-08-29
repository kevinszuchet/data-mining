import sys
import argparse
from tabulate import tabulate
from db.mysql_connector import MySQLConnector
from scrapper.nomad_list_scrapper import NomadListScrapper


# TODO handle abbreviations

class CommandLineInterface:
    def __init__(self):
        self._parser = argparse.ArgumentParser(description="This CLI controls the Nomad List Scrapper", prog="nls",
                                               epilog="Find more information at: https://github.com/jonatankruszewski/data-mining")
        self._load_parsers()
        self._sub_parser = self._parser.add_subparsers(dest="command")
        self._add_parsers()

        self._parse_args()

    def _load_parsers(self):
        # TODO: list of Parser instances
        self._parsers = {
            'scrape': {
                'method': CommandLineInterface.scrap_cities,
                'help_message': 'Scrap specific cities from the Nomad List site.',
                'params': [
                    {
                        'name': 'num-of-cities',
                        'positional': False,
                        'type': int,
                        'help': 'Number of required cities.'
                    },
                    {
                        'name': 'scrolls',
                        'positional': False,
                        'type': int,
                        'help': 'Number of scrolls to make in the site to fetch the cities cities.'
                    },
                    {
                        'name': 'verbose',
                        'positional': False,
                        'default': False,
                        'action': 'store_true',
                        'help': 'Verbosity level.'
                    }
                ]
            },
            'filter': {
                'method': CommandLineInterface.filter_by,
                'help_message': 'Fetch stored cities that match the filters.',
                'params': [
                    {
                        'name': 'num-of-cities',
                        'positional': False,
                        'type': int,
                        'help': 'Number of required cities.'
                    },
                    {
                        'name': 'country',
                        'positional': False,
                        'type': str,
                        'help': 'Name of the country.'
                    },
                    {
                        'name': 'continent',
                        'positional': False,
                        'type': str,
                        'help': 'Name of the continent.'
                    },
                    {
                        'name': 'rank-from',
                        'positional': False,
                        'type': int,
                        'help': 'From rank <rank-from>.'
                    },
                    {
                        'name': 'rank-to',
                        'positional': False,
                        'type': int,
                        'help': 'To rank <rank-to>.'
                    },
                    {
                        'name': 'sorted-by',
                        'positional': False,
                        'type': str,
                        'help': 'Sorting criteria.',
                        # TODO we could offer combinations (name, rank for example)
                        'choices': ['city_rank', 'name', 'country', 'continent', 'cost', 'internet', 'fun', 'safety'],
                        'default': 'city_rank'
                    },
                    {
                        'name': 'order',
                        'positional': False,
                        'type': str,
                        'help': 'Order of sorting.',
                        'choices': ['ASC', 'DESC'],
                        'default': 'ASC'
                    },
                    {
                        'name': 'verbose',
                        'positional': False,
                        'default': False,
                        'action': 'store_true',
                        'help': 'Verbosity level.'
                    }
                ]
            }
        }

    def _add_parsers(self):
        for command, parser in self._parsers.items():
            nested_parser = self._sub_parser.add_parser(command, help=parser['help_message'])
            for subcommand in parser['params']:
                argument_name = subcommand['name'] if subcommand['positional'] else f"--{subcommand['name']}"
                if subcommand.get('action'):
                    nested_parser.add_argument(argument_name, action=subcommand.get('action'), help=subcommand['help'])
                else:
                    nested_parser.add_argument(argument_name, type=subcommand['type'],
                                               choices=subcommand.get('choices'),
                                               default=subcommand.get('default'),
                                               nargs=subcommand.get('nargs'),
                                               help=subcommand['help'])

    def _parse_args(self):
        inputs = vars(self._parser.parse_args())
        command = inputs['command']
        inputs.pop('command')

        if not command:
            self._parser.print_help()
            sys.exit(0)

        self._parsers[command]['method'](**inputs)

    @staticmethod
    def scrap_cities(*args, **kwargs):
        NomadListScrapper()
        return MySQLConnector().sort_cities_by(*args, **kwargs)

    @staticmethod
    def filter_by(*args, **kwargs):
        results = MySQLConnector().filter_cities_by(*args, **kwargs)
        print(tabulate(results, headers=['Rank', 'City', 'Country', 'Continent']), end='\n\n')


if __name__ == "__main__":
    CommandLineInterface()
