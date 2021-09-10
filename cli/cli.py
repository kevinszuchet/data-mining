import sys
import argparse, argcomplete
from logger import Logger
from cli.parser import SetupSchemasParser, ScrapeParser, ShowParser
from pymysql.err import OperationalError

UNKNOWN_DATABASE = 1049


class CommandLineInterface:
    """Class that handles the user interactions with the scrapper and the MySQL database via the command line."""

    def __init__(self):
        epilog = "Find more information at: https://github.com/kevinszuchet/data-mining"
        self._parser = argparse.ArgumentParser(description="This CLI controls the Nomad List Scrapper", prog="nls",
                                               epilog=epilog,
                                               allow_abbrev=False)
        self._parsers = {'setup-db': SetupSchemasParser(), 'scrape': ScrapeParser(), 'show': ShowParser()}
        self._sub_parser = self._parser.add_subparsers(dest="command")
        self._add_parsers()
        argcomplete.autocomplete(self._parser)
        self._parse_args()

    def _add_parsers(self):
        """Creates a nested parser for each command in the parsers dictionary,
        and add the necessary arguments to interact with it using that command line."""
        for command, parser in self._parsers.items():
            nested_parser = self._sub_parser.add_parser(command, help=parser.help_message())
            parser.add(nested_parser)

    def _parse_args(self):
        """Parse the arguments introduced by the users, and calls the necessary parser to handle those arguments."""
        inputs = vars(self._parser.parse_args())
        command = inputs['command']
        inputs.pop('command')

        verbose = inputs.get('verbose')
        logger = Logger(verbose=verbose).logger


        if not command:
            self._parser.print_help()
            sys.exit(0)

        try:
            self._parsers[command].parse(**inputs)
        except OperationalError as e:
            code, message = e.args

            if code == UNKNOWN_DATABASE:
                logger.error(f"You should run the setup-db command before start scraping the cities.", exc_info=verbose)
                sys.exit(1)

            logger.error(f"MySQL Operational Exception raised: {e}", exc_info=verbose)
            sys.exit(1)
        except Exception as e:
            logger.error(f"Exception raised: {e}", exc_info=verbose)
            sys.exit(1)


if __name__ == "__main__":
    CommandLineInterface()
