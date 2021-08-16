import pymysql
from conf import MYSQL


class MySQLConnector:
    """Class that knows how to handle the connection with MySQL."""

    def __init__(self, logger):
        self._logger = logger
        self._client = self._connection()

    @staticmethod
    def _connection():
        """Knows how to connect to the MySQL Database."""
        conn_info = {'host': MYSQL.host, 'user': MYSQL.user, 'password': MYSQL.password, 'database': MYSQL.database}
        return pymysql.connect(**conn_info)

    def insert_city_info(self, city):
        """Given the city, inserts all the necessary rows in the DB to store the scrapped data."""
        pass
