import sys
import argparse
from logger import Logger
from cli.parser import SetupSchemasParser, ScrapeParser, FilterParser


class CommandLineInterface:
    def __init__(self):
        epilog = "Find more information at: https://github.com/kevinszuchet/data-mining"
        self._parser = argparse.ArgumentParser(description="This CLI controls the Nomad List Scrapper", prog="nls",
                                               epilog=epilog,
                                               allow_abbrev=False)
        self._parsers = {'setup-db': SetupSchemasParser(), 'scrape': ScrapeParser(), 'filter': FilterParser()}
        self._sub_parser = self._parser.add_subparsers(dest="command")
        self._add_parsers()

        self._parse_args()

    def _add_parsers(self):
        for command, parser in self._parsers.items():
            nested_parser = self._sub_parser.add_parser(command, help=parser.help_message())
            parser.add(nested_parser)

    def _parse_args(self):
        inputs = vars(self._parser.parse_args())
        command = inputs['command']
        inputs.pop('command')

        if not command:
            self._parser.print_help()
            sys.exit(0)

        try:
            self._parsers[command].parse(**inputs)
        except Exception as e:
            Logger(verbose=inputs.get('verbose')).error(f"Exception raised: {e}", exc_info=inputs.get('verbose'))
            sys.exit(1)


if __name__ == "__main__":
    CommandLineInterface()
