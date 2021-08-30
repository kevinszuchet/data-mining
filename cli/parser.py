from tabulate import tabulate
from db.mysql_connector import MySQLConnector
from scrapper.nomad_list_scrapper import NomadListScrapper

OPTIONAL_KWARGS = ['type', 'action', 'choices', 'default']
VERBOSE_PARAM = {'name': 'verbose,v', 'positional': False, 'action': 'store_true', 'help': 'Verbosity level.'}


class Parser:
    """Abstract class for the parsers who knows how to handle the different CLI commands."""

    def __init__(self, help_message, params=None):
        if params is None:
            params = []

        self._params = [*params, VERBOSE_PARAM]
        self._help_message = help_message

    def _argument_names(self, subcommand):
        names = subcommand['name'].split(',')

        if subcommand['positional']:
            return names

        return [f"--{name}" if len(name) > 1 else f"-{name}" for name in names]

    def _argument_kwargs(self, subcommand):
        return {opt: subcommand.get(opt) for opt in OPTIONAL_KWARGS if subcommand.get(opt)}

    def help_message(self):
        return self._help_message

    def parse(self, *args, **kwargs):
        """Abstract implementation of the parser behaviour."""
        pass

    def add(self, nested_parser):
        for subcommand in self._params:
            nested_parser.add_argument(*self._argument_names(subcommand), **self._argument_kwargs(subcommand),
                                       help=subcommand['help'])


class SetupSchemasParser(Parser):
    """Parser that knows how to set up the MySQL schemas."""

    def __init__(self):
        super().__init__(help_message='Create the necessary schemas to store the scrape data into a MySQL database.')

    def parse(self, *args, **kwargs):
        MySQLConnector.create_database(*args, **kwargs)


class ScrapeParser(Parser):
    """Parser that knows how to scrape the cities using the NomadListScrapper."""

    def __init__(self):
        params = [
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
            }
        ]
        super().__init__(params=params, help_message='Scrap specific cities from the Nomad List site.')

    def parse(self, *args, **kwargs):
        NomadListScrapper(verbose=kwargs.get('verbose')).scrap_cities(*args, **kwargs)


class FilterParser(Parser):
    """Parser that knows how to use the MySQL connector to filter and sort the scrapped data."""

    def __init__(self):
        params = [
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
            }
        ]
        super().__init__(params=params, help_message='Fetch stored cities that match the filters.')

    def parse(self, *args, **kwargs):
        with MySQLConnector(verbose=kwargs.get('verbose')) as mysql_connector:
            results = mysql_connector.filter_cities_by(*args, **kwargs)
            print(tabulate(results, headers=['Rank', 'City', 'Country', 'Continent']), end='\n\n')
