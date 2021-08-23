import argparse


# TODO handle abbreviations

class CommandLineInterface:
    def __init__(self):
        self._parser = argparse.ArgumentParser(description="This CLI controls the Nomad List Scrapper", prog="nlsctl",
                                               epilog="Find more information at: https://github.com/jonatankruszewski/data-mining")
        self._load_parsers()
        self._sub_parser = self._parser.add_subparsers(dest="command")
        self._add_parsers()

        inputs = vars(self._parser.parse_args())
        command = inputs['command']
        inputs.pop('command')

        try:
            result = self._parsers[command]['method'](**inputs)
            print(result)
        except (FileNotFoundError, OSError, TypeError, ValueError) as e:
            print('An error occurred:')
            print(f"\t{e}")
        except KeyError:
            print('An error occurred:')
            print(f"\tPlease provide one command at least. Refer to help for further assistance")

    def _load_parsers(self):
        self._parsers = {
            'filter': {
                'method': CommandLineInterface.filter_by,
                'help_message': 'Take specific cities that match the filters.',
                'params': [
                    {
                        'name': 'scrolls',
                        'positional': False,
                        'type': int,
                        'help': 'Number of scrolls to take the cities.'
                    },
                    {
                        'name': 'num',
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
                    }
                ]
            },
            'sort': {
                'method': CommandLineInterface.sort_by,
                'help_message': 'Sort the scrapped cities by some criteria.',
                'params': [
                    {
                        'name': 'by',
                        'positional': False,
                        'type': str,
                        'help': 'Sorting criteria.',
                        # TODO we may offer combinations (name, rank for example)
                        'choices': ['rank', 'name', 'country', 'continent']
                    },
                    {
                        'name': 'order',
                        'positional': True,
                        'type': str,
                        'help': 'Order of sorting.',
                        'choices': ['ASC', 'DESC'],
                        'default': 'ASC'
                    }
                ]
            }
        }

    def _add_parsers(self):
        for command, parser in self._parsers.items():
            nested_parser = self._sub_parser.add_parser(command, help=parser['help_message'])
            for subcommand in parser['params']:
                argument_name = subcommand['name'] if subcommand['positional'] else f"--{subcommand['name']}"
                nested_parser.add_argument(argument_name, type=subcommand['type'], choices=subcommand.get('choices'),
                                           default=subcommand.get('default'),
                                           help=subcommand['help'])

    @staticmethod
    def filter_by(*args, **kwargs):
        print("Hi! I'm a filter", args, kwargs)

    @staticmethod
    def sort_by(*args, **kwargs):
        print("Hi! I'm a sort by", args, kwargs)


if __name__ == "__main__":
    CommandLineInterface()
