import logging
import sys
from conf import LOG_FORMAT, LOG_FILE, LOGGER_LEVEL

LOGGER = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}


class Logger:
    def __init__(self, logger_level=LOGGER_LEVEL, verbose=False):
        # Initiating the logger object
        self.logger = logging.getLogger(__name__)

        if verbose:
            logger_level = 'DEBUG'

        # Set the level of the logger.
        self.logger.setLevel(LOGGER.get(logger_level, logging.ERROR))

        # Format the logs structure so that every line would include the time, name, level name and log message
        formatter = logging.Formatter(LOG_FORMAT)

        # Create a file handler and add it to logger
        file_handler = logging.FileHandler(LOG_FILE)

        # file_handler.setLevel(logging.ERROR)
        file_handler.setFormatter(formatter)

        # Create a stream handler and add it to logger
        stream_handler = logging.StreamHandler(sys.stdout)
        # stream_handler.setLevel(logging.ERROR)
        stream_handler.setFormatter(formatter)

        # Avoid duplicating logs
        if self.logger.hasHandlers():
            self.logger.handlers.clear()

        self.logger.addHandler(file_handler)
        self.logger.addHandler(stream_handler)
