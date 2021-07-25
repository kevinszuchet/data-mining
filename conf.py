""" Config file with parameters. """

import os

NOMAD_LIST_URL = "https://nomadlist.com"
NOMAD_LIST_SCROLL_PAUSE_TIME = 10
NOMAD_LIST_DELAY_AFTER_REQUEST = 10

CHROME_DRIVER_PATH = os.getenv('CHROME_DRIVER_PATH')

LOG_FILE = "logs.log"
LOG_FORMAT = '%(asctime)s-%(levelname)s-FILE:%(filename)s-FUNC:%(funcName)s-LINE:%(lineno)d-%(message)s'

JSON_FILENAME = "data.json"
