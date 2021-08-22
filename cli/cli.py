import argparse
from parsers import PARSERS


class CommandLineInterface:
    def __init__(self):
        self._parser = argparse.ArgumentParser()
        self._sub_parser = self.parser.add_subparsers(dest="command")
        self._add_parsers()

        inputs = vars(self._parser.parse_args())
        command = inputs['command']
        inputs.pop('command')

        try:
            result = PARSERS[command]['method'](**inputs)
            print(result)
        except (FileNotFoundError, OSError, TypeError, ValueError) as e:
            print('An error occurred:')
            print(f"\t{e}")
        except KeyError:
            print('An error occurred:')
            print(f"\tPlease provide one command at least. Refer to help for further assistance")

    def _add_parsers(self):
        for command, parser in PARSERS.items():
            nested_parser = self._sub_parser.add_parser(command, help=parser['help_msg'])
            for subcommand in parser['params']:
                argument_name = subcommand['name'] if subcommand['positional'] else f"--{subcommand['name']}"
                nested_parser.add_argument(argument_name, type=subcommand['type'], choices=subcommand.get('choices'),
                                           help=subcommand['help'])

    def filter_by(self, *args, **kwargs):
        print("Hi! I'm a filter", args, kwargs)

    def sort_by(self, *args, **kwargs):
        print("Hi! I'm a sort by", args, kwargs)
