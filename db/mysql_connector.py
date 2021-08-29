import pymysql
from functools import reduce
from conf import MYSQL
from logger import Logger
import re


class MySQLConnector:
    """Class that knows how to handle the connection with MySQL."""

    def __init__(self, logger=Logger().logger):
        # TODO: singleton to save the ids of the tabs in a Class dict
        self._logger = logger
        self._client = self._connection()

    def _connection(self):
        """Knows how to connect to the MySQL Database."""
        conn_info = {'host': MYSQL['host'], 'user': MYSQL['user'], 'password': MYSQL['password'],
                     'database': MYSQL['database']}
        self._logger.info("Connecting to the MySQL database...")
        return pymysql.connect(**conn_info)

    def _create_database(self):
        """Creates the MySQL Nomadlist Schema in which to store all the scrapped data."""
        # TODO CLI: mysql -u root -p < create_schemas.sql
        try:
            with open('create_schemas.sql, 'r'') as sql_code_file:
                with self._client.cursor() as cursor:
                    cursor.execute(sql_code_file.read(), multi=True)
                    self._client.commit()
        except Error as e:
            print(e)

    def _upsert_and_get_id(self, table, values_dict, domain_identifier=None):
        """
            Upsert a row in a table, and returns the id of it.
            @param table: Name of the SQL table.
            @param values_dict: Dictionary with column names as keys, and values as values of the dictionary.
            @param domain_identifier: The way to identify a row of the table in the domain (str|list|tuple).

            @return: Id of the upserted row.

            Given the table name, the values to upsert, and the optional domain_identifier,
            tries to update the row in the table, unless it doesn't exist. If that happens, then inserts the row,
            and returns its id.
        """

        columns = ', '.join(values_dict.keys())

        filters = [f"{key} = '{value}'" for key, value in values_dict.items() if
                   domain_identifier is None or key == domain_identifier or key in domain_identifier]
        where_clause = ' AND'.join(filters)
        select_query = f"SELECT id, {columns} FROM {table} WHERE {where_clause};"

        values_tuple = tuple(values_dict.values())

        insert_query = f"""
        INSERT IGNORE INTO {table}
        ({columns})
        VALUES ({', '.join(['%s'] * len(values_dict))})
        """

        update_query = f"""
        UPDATE TABLE {table}
        SET ({', '.join([f"{key} = '{value}'" for key, value in values_dict.items()])})
        """

        with self._client.cursor() as cursor:
            self._logger.info(f"Selecting the id of one of the {table}...")
            self._logger.debug(select_query)
            cursor.execute(select_query)
            result = cursor.fetchone()
            self._logger.debug(f"Result of the query: {result}")

            if result:
                row_id, *other_values = result
                differences = [other_value != values_tuple[i] for i, other_value in enumerate(other_values)]

                if any(differences):
                    self._logger.info(f"There are differences between the old and the new row. About to update it...")
                    self._logger.debug(update_query)
                    cursor.execute(update_query)
                    self._client.commit()

                return row_id

            self._logger.info(f"Inserting the new row in the table {table}...")
            self._logger.debug(f"Query: {insert_query} - Values: {values_tuple}")
            cursor.execute(insert_query, values_tuple)
            self._client.commit()
            row_id = cursor.lastrowid

        return row_id

    def _upsert_tab_and_attributes(self, tab_name, tab_info):
        """
        Given the name of the tab, and its information, takes all the attributes,
        then creates the rows for the tab table and the attributes one.
        Returns all the ids of those upserted attributes.

        @param tab_name: Name of the tab.
        @param tab_info: Tab information.
        """

        insert_tabs_query = "INSERT IGNORE INTO tabs (name) VALUES (%s)"
        insert_attributes_query = "INSERT IGNORE INTO attributes (name, id_tab) VALUES (%s, %s)"

        with self._client.cursor() as cursor:
            # TODO: insert only once all the tabs names.
            self._logger.debug(f"Trying to insert a new tab {tab_name}")
            cursor.execute(insert_tabs_query, tab_name)
            self._client.commit()

            # Selecting the id of the tab name {tab_name}
            cursor.execute(f"SELECT id FROM tabs WHERE name = '{tab_name}';")
            id_tab, = cursor.fetchone()

            # Inserting ATTRIBUTE NAMES into attributes table
            self._logger.info(f"Inserting attributes for the tab {tab_name}...")
            values = [(attribute, id_tab) for attribute in tab_info.keys()]
            self._logger.debug(f"Query: {insert_attributes_query} - Values: {values}")
            cursor.executemany(insert_attributes_query, values)
            self._client.commit()

            # Selecting the ids of the ATTRIBUTE NAMES
            cursor.execute(f"SELECT id, name FROM attributes WHERE id_tab = {id_tab};")
            attributes = cursor.fetchall()
        return attributes

    def _upsert_key_value_tab_info(self, id_city, tab_name, tab_info):
        """
        Given the name of the table, and the values to insert, tries to insert or update the rows into the tab's table.

        @param id_city: Id of the current city.
        @param tab_name: Name of the tab.
        @param tab_info: Tab information.
        """

        insert_city_attributes_query = """
        INSERT INTO city_attributes
        (id_city, id_attribute, description)
        -- value, url 
        VALUES (%s, %s, %s) as new
            ON DUPLICATE KEY UPDATE 
                description = new.description 
                -- value = new.value, url = new.url
        """

        attributes = self._upsert_tab_and_attributes(tab_name, tab_info)

        with self._client.cursor() as cursor:
            # Inserting {tab_name} ATTRIBUTE VALUES into city_attributes table
            self._logger.info(f"Inserting the value of the attributes for the tab {tab_name}...")
            values = [(id_city, id_attribute, tab_info.get(attribute))
                      for id_attribute, attribute in attributes if tab_info.get(attribute)]
            self._logger.debug(f"Query: {insert_city_attributes_query} - Values: {values}")
            cursor.executemany(insert_city_attributes_query, values)
            self._client.commit()

    def _upsert_weather(self, id_city, details):
        """
        Given the id and the details of the city, insert all the weather information in the database..

        @param id_city: Id of the current city.
        @param details: Details of the city to take the info of the weather tab.
        """

        insert_monthly_weathers_attributes_query = """
        INSERT INTO monthly_weathers_attributes
        (id_city, id_attribute, month, value)
        -- description
        VALUES (%s, %s, %s, %s) as new
            ON DUPLICATE KEY UPDATE 
                value = new.value
                -- description = new.description
        """

        tab_name = 'Weather'
        tab_info = details['Weather']

        attributes = self._upsert_tab_and_attributes(tab_name, tab_info)

        with self._client.cursor() as cursor:
            # Inserting ATTRIBUTE VALUES into monthly_weathers_attributes table
            self._logger.info(f"Inserting the value of the attributes for the tab Weather...")
            values = [(id_city, id_attribute, i + 1, value)
                      for id_attribute, attribute in attributes
                      for i, [__, value] in enumerate(tab_info.get(attribute, []))]
            self._logger.debug(f"Query: {insert_monthly_weathers_attributes_query} - Values: {values}")
            cursor.executemany(insert_monthly_weathers_attributes_query, values)
            self._client.commit()

    def _upsert_many(self, table, id_city, columns, values):
        """
        Given the table, the id of the city, and the values to insert, upserts the values into the table.

        @param table: Name of the table in the Database.
        @param id_city: Id of the current city.
        @param columns: List of the columns to fill with the values list. It's not necessary to add the id_city column.
        @param values: List of tuples with values to insert into the table.
        """

        columns = ['id_city'] + columns
        values_template = ', '.join(['%s'] * len(columns))
        insert_query = f"INSERT IGNORE INTO {table} ({', '.join(columns)}) VALUES ({values_template})"

        with self._client.cursor() as cursor:
            self._logger.info(f"Upserting many values of the table {table}...")
            values = [(id_city,) + (tuple_of_values if isinstance(tuple_of_values, tuple) else (tuple_of_values,))
                      for tuple_of_values in values]
            self._logger.debug(f"Query: {insert_query} - Values: {values}")
            cursor.executemany(insert_query, values)
            self._client.commit()

    def _insert_relationships(self, id_city, details):
        """
        Given the id of the current city and the details of it, insert the relationships between this city and the near,
        next, or similar to it.

        @param id_city: Id of the current city.
        @param details: Dictionary with all the information about the current city.
        """

        types = ['Near', 'Next', 'Similar']
        cities = set(reduce(lambda cities_names, key: cities_names + details[key], types, []))

        insert_cities_query = "INSERT IGNORE INTO cities (name) VALUES (%s)"
        selectable_cities = ','.join([f"'{city}'" for city in cities])
        select_cities_query = f"SELECT id, name FROM cities WHERE name IN ({selectable_cities})"

        insert_cities_relationships_query = """
        INSERT IGNORE INTO cities_relationships
        (id_city, id_related_city, type)
        VALUES (%s, %s, %s)
        """

        with self._client.cursor() as cursor:
            self._logger.info(f"Inserting cities related to the current one...")
            cursor.executemany(insert_cities_query, cities)
            self._client.commit()

            cursor.execute(select_cities_query)
            relationships = []
            for id_related, name in cursor.fetchall():
                for i, type_name in enumerate(types):
                    if name in details[type_name]:
                        relationships.append((id_city, id_related, i))

            self._logger.info(f"Inserting all the city relationships...")
            self._logger.debug(f"Query: {insert_cities_relationships_query} - Values: {relationships}")
            cursor.executemany(insert_cities_relationships_query, relationships)
            self._client.commit()

    def insert_city_info(self, details):
        """Given the details of the city, insert all the necessary rows to store it in the database."""

        id_continent = self._upsert_and_get_id("continents", {'name': details['continent']},
                                               domain_identifier='name')

        country = {'name': details['country'], 'id_continent': id_continent}
        id_country = self._upsert_and_get_id("countries", country, domain_identifier='name')

        city = {'name': details['city'], 'city_rank': details['rank'], 'id_country': id_country}
        id_city = self._upsert_and_get_id("cities", city, domain_identifier='name')

        self._upsert_key_value_tab_info(id_city, 'Scores', details['Scores'])
        self._upsert_key_value_tab_info(id_city, 'Digital Nomad Guide', details['DigitalNomadGuide'])
        self._upsert_key_value_tab_info(id_city, 'Cost of Living', details['CostOfLiving'])

        self._upsert_many('photos', id_city, ['src'], details['Photos'])

        pros_and_cons = details['ProsAndCons']
        pros = [(pro, 'P') for pro in pros_and_cons['pros']]
        cons = [(con, 'C') for con in pros_and_cons['cons']]
        # TODO: think how to avoid inserting duplicate rows without using the description as a UNIQUE constraint
        self._upsert_many('pros_and_cons', id_city, ['description', 'type'], pros + cons)

        # TODO scrap date
        # TODO insert only new data (using review date)
        self._upsert_many('reviews', id_city, ['description'], details['Reviews'])

        self._upsert_weather(id_city, details)

        self._insert_relationships(id_city, details)

    def filter_cities_by(self, *args, num_of_cities=None, country=None, continent=None, rank_from=None, rank_to=None,
                         sorted_by, order, **kwargs):
        """Given the filter criteria, build a query to fetch the required cities from the database."""

        query = f"""
            SELECT city.city_rank, city.name, country.name, continent.name  
            FROM cities city
            JOIN countries country ON city.id_country = country.id
            JOIN continents continent ON country.id_continent = continent.id
            {'WHERE' if country or continent or rank_from or rank_to else ''}
                {f'country.name = {country} AND ' if country else ''}
                {f'continent.name = {continent} AND ' if continent else ''}
                {f'rank >= {rank_from} AND ' if rank_from else ''}
                {f'rank <= {rank_to} AND ' if rank_to else ''}
            ORDER BY {sorted_by} {order}
            {f'LIMIT {num_of_cities}' if num_of_cities else ''}
            ;"""

        query = "\n".join([re.sub(" +", " ", s) for s in filter(str.strip, query.splitlines())])

        self._logger.debug(f"About to execute the filter query: {query}")

        with self._client.cursor() as cursor:
            self._logger.info("Executing the query with all the filters...")

            cursor.execute(query)
            result = cursor.fetchall()

            self._logger.debug(f"Execution results: {result}")

        return result
