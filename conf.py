""" Config file with parameters. """

import os
from dotenv import load_dotenv

load_dotenv()

NOMAD_LIST_URL = "https://nomadlist.com"
NOMAD_LIST_SCROLL_PAUSE_TIME = 2
NOMAD_LIST_DELAY_AFTER_REQUEST = 2
NOMAD_LIST_REQUESTS_BATCH_SIZE = 20

CHROME_DRIVER_PATH = os.getenv('NOMAD_LIST_CHROME_DRIVER_PATH')

LOG_FILE = "logs.log"
LOG_FORMAT = '%(asctime)s-%(levelname)s-FILE:%(filename)s-FUNC:%(funcName)s-LINE:%(lineno)d-%(message)s'

JSON_FILENAME = "data.json"
LOGGER_LEVEL = "DEBUG"
PAGE_SOURCE = "page_source.html"
LOAD_HTML_FROM_DISK = False
SCROLL = True
HEADERS = {
    'user-agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36",
    'cookie': "ref=weremoto; visit-count=1; last_tested_internet_speed=2020-03-13_x; __stripe_mid=0adfa558-f217-49fe-8f7c-7c769760f498b8f7c4; visit-count=2; login_by_email_client_hash=6e693f5e751a957575c6c6bd664bba4a; login_url=https://nomadlist.com/?join=nomadlist; logged_in_hash=fccb1ad6e406b0111d55512cad8ae099_4885b578c08d502e2c6b6ae23d523bb26949c16e; ask_to_connect_instagram_hide=x; filters-folded=no; dark_mode=on; dark_mode_js_test=on; PHPSESSID=nba5obbj3eb9qn9pe2ch25evi1; last_tested_internet_speed=2021-07-25_x"
}

MYSQL = {
    'host': os.getenv('NOMAD_LIST_MYSQL_HOST') or 'localhost',
    'user': os.getenv('NOMAD_LIST_MYSQL_USER') or 'root',
    'password': os.getenv('NOMAD_LIST_MYSQL_PASSWORD') or '',
    'database': os.getenv('NOMAD_LIST_MYSQL_DATABASE') or 'nomad_list'
}
