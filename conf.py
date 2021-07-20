""" Config file with parameters. """

import os

NOMAD_LIST_URL = "https://nomadlist.com"
NOMAD_LIST_SCROLL_PAUSE_TIME = 10

PATH_TO_WEB_DRIVER = os.getenv('PATH_TO_WEB_DRIVER')

LOG_FILE = "logs.log"
LOG_FORMAT = '%(asctime)s-%(levelname)s-FILE:%(filename)s-FUNC:%(funcName)s-LINE:%(lineno)d-%(message)s'
