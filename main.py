import sys
from logger import Logger
from cli.cli import CommandLineInterface


def main():
    try:
        CommandLineInterface()
    except Exception as e:
        Logger().logger.error(f"Exception raised: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
