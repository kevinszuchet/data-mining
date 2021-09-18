import json
import csv
from tabulate import tabulate
from db.mysql_connector import MySQLConnector
from scrapper.nomad_list_scrapper import NomadListScrapper
from apis.aviation_stack import AviationStackAPI

OPTIONAL_KWARGS = ['type', 'action', 'choices', 'default']
VERBOSE_PARAM = {'name': 'verbose,v', 'positional': False, 'action': 'store_true', 'help': 'Enable verbosity.'}


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
        params = [{
            'name': 'force,f',
            'positional': False,
            'action': 'store_true',
            'help': 'Force the database creation dropping all the existing schemas, and creating them all again. Use it carefully.'
        }]
        super().__init__(params=params,
                         help_message='Create the necessary schemas to store the scrape data into a MySQL database.')

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


class ShowParser(Parser):
    """Parser that knows how to use the MySQL connector to filter and sort the scrapped data.
    Then, it shows the data in a table format."""

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
                'type': str.lower,
                'help': 'Sorting criteria. Default: rank.',
                'choices': ['rank', 'name', 'country', 'continent', 'overall score', 'cost', 'internet', 'fun',
                            'safety'],
                'default': 'rank'
            },
            {
                'name': 'order',
                'positional': False,
                'type': str,
                'help': 'Order of sorting. Default: ASC.',
                'choices': ['ASC', 'DESC'],
                'default': 'ASC'
            },
            {
                'name': 'output,o',
                'positional': False,
                'type': str.lower,
                'choices': ['table', 'json', 'csv'],
                'default': 'table',
                'help': 'Output format. Default: table.'
            },
        ]
        self._headers = ['Rank', 'City', 'Country', 'Continent', '⭐ Overall Score', '💵 Cost', '📡 Internet', '😀 Fun',
                         '👮 Safety']
        super().__init__(params=params, help_message='Fetch and show stored cities that match the filters.')

    def parse(self, *args, **kwargs):
        presenters = {'table': self._to_table, 'json': self._to_json, 'csv': self._to_csv}

        with MySQLConnector(verbose=kwargs.get('verbose')) as mysql_connector:
            results = mysql_connector.filter_cities_by(*args, **kwargs)

        presenter = presenters.get(kwargs.get('output'), presenters['table'])
        print('\n\n' + presenter(results), end='\n\n')

    def _to_table(self, results):
        return tabulate(results, headers=self._headers)

    def _to_json(self, results):
        results_list = [{self._headers[i].split(" ", 1)[-1]: value for i, value in enumerate(row)} for row in results]
        return json.dumps(results_list, indent=4)

    def _to_csv(self, results):
        headers = ','.join(self._headers)
        rows = [','.join(map(str, row)) for row in results]
        return '\n'.join([headers] + rows)


class AviationStackParser(Parser):
    """Parser that knows how to interact with the Aviation Stack API."""

    def __init__(self):
        params = [
            {
                'name': 'resource,r',
                'positional': False,
                'type': str.lower,
                'help': 'Name of the desired resource.',
                'choices': ['countries', 'cities', 'airports']
            }
        ]
        super().__init__(params=params, help_message='Calls the correspondent endpoints of the API.')

    def parse(self, *args, **kwargs):
        resource = kwargs.get('resource')
        api = AviationStackAPI()
        methods = {'countries': api.countries, 'cities': api.cities, 'airports': api.airports}
        method = methods.get(kwargs.get('resource'))
        res = None

        if method:
            res = method()

        print(res)
