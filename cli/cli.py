import sys
import argparse
from tabulate import tabulate
from db.mysql_connector import MySQLConnector
from logger import Logger
from scrapper.nomad_list_scrapper import NomadListScrapper


# TODO verbose implies a higher level of logs

class CommandLineInterface:
    optional_kwargs = ['type', 'action', 'choices', 'default']

    def __init__(self):
        epilog = "Find more information at: https://github.com/kevinszuchet/data-mining"
        self._parser = argparse.ArgumentParser(description="This CLI controls the Nomad List Scrapper", prog="nls",
                                               epilog=epilog,
                                               allow_abbrev=False)
        self._load_parsers()
        self._sub_parser = self._parser.add_subparsers(dest="command")
        self._add_parsers()

        self._parse_args()

    def _load_parsers(self):
        # TODO: list of Parser instances
        self._parsers = {
            'setup-db-schemas': {
                'method': CommandLineInterface.setup_db,
                'help_message': 'Create the necessary schemas to store the scrape data into a MySQL database.',
                'params': [
                    {
                        'name': 'verbose,v',
                        'positional': False,
                        'action': 'store_true',
                        'help': 'Verbosity level.'
                    }
                ]
            },
            'scrape': {
                'method': CommandLineInterface.scrap_cities,
                'help_message': 'Scrap specific cities from the Nomad List site.',
                'params': [
                    {
                        'name': 'num-of-cities,n',
                        'positional': False,
                        'type': int,
                        'help': 'Number of required cities.'
                    },
                    {
                        'name': 'scrolls,s',
                        'positional': False,
                        'type': int,
                        'help': 'Number of scrolls to make in the site to fetch the cities cities.'
                    },
                    {
                        'name': 'verbose,v',
                        'positional': False,
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
                        'name': 'num-of-cities,n',
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
                        'choices': ['rank', 'name', 'country', 'continent', 'cost', 'internet', 'fun', 'safety'],
                        'default': 'rank'
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
                        'name': 'verbose,v',
                        'positional': False,
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
                names = subcommand['name'].split(',')
                argument_names = names if subcommand['positional'] else [f"--{name}" if len(name) > 1 else f"-{name}"
                                                                         for name in names]
                kwargs = {opt: subcommand.get(opt) for opt in self.optional_kwargs if subcommand.get(opt)}
                nested_parser.add_argument(*argument_names, **kwargs, help=subcommand['help'])

    def _parse_args(self):
        inputs = vars(self._parser.parse_args())
        command = inputs['command']
        inputs.pop('command')

        if not command:
            self._parser.print_help()
            sys.exit(0)

        try:
            self._parsers[command]['method'](**inputs)
        except Exception as e:
            Logger(verbose=inputs.get('verbose')).error(f"Exception raised: {e}", exc_info=inputs.get('verbose'))
            sys.exit(1)

    @staticmethod
    def setup_db(*args, **kwargs):
        MySQLConnector(verbose=kwargs.get('verbose')).create_database(*args, **kwargs)

    @staticmethod
    def scrap_cities(*args, **kwargs):
        NomadListScrapper(verbose=kwargs.get('verbose')).scrap_cities(*args, **kwargs)

    @staticmethod
    def filter_by(*args, **kwargs):
        results = MySQLConnector(verbose=kwargs.get('verbose')).filter_cities_by(*args, **kwargs)
        print(tabulate(results, headers=['Rank', 'City', 'Country', 'Continent']), end='\n\n')


if __name__ == "__main__":
    CommandLineInterface()
