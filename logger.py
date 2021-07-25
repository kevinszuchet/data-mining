import logging
import sys
from conf import LOG_FORMAT, LOG_FILE


class Logger:
    def __init__(self):
        # Initiating the logger object
        self.logger = logging.getLogger(__name__)

        # Set the level of the logger.
        self.logger.setLevel(logging.DEBUG)

        # Format the logs structure so that every line would include the time, name, level name and log message
        formatter = logging.Formatter(LOG_FORMAT)

        # Create a file handler and add it to logger
        file_handler = logging.FileHandler(LOG_FILE)
        # file_handler.setLevel(logging.ERROR)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        # Create a stream handler and add it to logger
        stream_handler = logging.StreamHandler(sys.stdout)
        # stream_handler.setLevel(logging.ERROR)
        stream_handler.setFormatter(formatter)
        self.logger.addHandler(stream_handler)
