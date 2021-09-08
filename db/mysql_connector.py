import pymysql
import re
from functools import reduce
from conf import MYSQL
from logger import Logger
from datetime import datetime


# TODO: we could avoid all the selections and inserts statements with the tabs and attributes...
# TODO: Singleton with a dict of tabs and attributes keys.

class MySQLConnector:
    """Class that knows how to handle the connection with MySQL."""

    continents_cache = dict()
    countries_cache = dict()
    tabs_cache = dict()

    def __init__(self, logger=None, verbose=False):
        if logger is None:
            logger = Logger(verbose=verbose).logger
        self._logger = logger

    def __enter__(self):
        """Creates the connection when someone uses the with statement."""
        self._connection = pymysql.connect(host=MYSQL['host'], user=MYSQL['user'], password=MYSQL['password'],
                                           database=MYSQL['database'])
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Closes the connection to the SQL database."""
        self._connection.close()

    @staticmethod
    def create_database(*args, **kwargs):
        """Creates the MySQL NomadList Schema in which to store all the scrapped data."""

        logger = Logger(verbose=kwargs.get('verbose')).logger
        connection = pymysql.connect(host=MYSQL['host'], user=MYSQL['user'], password=MYSQL['password'])
        force = kwargs.get('force', False)

        logger.info("Connection to the MySQL host opened!")

        with connection:
            logger.info("About to read the SQL file to create the schemas...")
            with open('create_schemas.sql', 'r') as sql_code_file:
                script_file = sql_code_file.read()

            logger.info(f"The file was read.")

            with connection.cursor() as cursor:
                statements = script_file.split(';')
                logger.debug(f"Cursor created. Now, it's time to execute the {len(statements)} different statements.")
                for statement in statements:
                    if not statement.strip():
                        continue

                    if statement.lower().strip().startswith('drop') and not force:
                        continue

                    # Would it be necessary to log the statements?
                    # logger.debug(f"Executing the follow statement...\n{statement}")
                    cursor.execute(statement)
                    connection.commit()

            logger.info("Script successfully executed!")

    def _upsert_continent_and_get_id(self, details):
        """
        Given the details of the city, takes the name of the continent and tries to take the id using the cache.
        If the continent hasn't been added yet, it will be created first in the DB and then added to the dict.
        It returns the id of the continent.
        """
        continent = details.get('continent')

        if continent in self.continents_cache:
            self._logger.debug(f"The continent {continent} was created before, taking the id from the cache...")
            return self.continents_cache.get(continent)

        values_dict = {'name': details.get('continent')}
        id_continent = self._upsert_and_get_id("continents", values_dict, domain_identifier='name')
        self.continents_cache.update({continent: id_continent})
        return id_continent

    def _upsert_country_and_get_id(self, id_continent, details):
        """
        Given the id of the continent, details of the city, takes the name of the country and tries to take the id
        from the cache. If it hasn't been added yet, it will be created first in the DB and then added to the dict.
        It returns the id of the country.
        """
        country = details.get('country')

        if country in self.countries_cache:
            self._logger.debug(f"The country {country} was created before, taking the id from the cache...")
            return self.countries_cache.get(country)

        values_dict = {'name': country, 'id_continent': id_continent}
        id_country = self._upsert_and_get_id("countries", values_dict, domain_identifier='name')
        self.countries_cache.update({country: id_country})
        return id_country

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

        filters = [(key, value) for key, value in values_dict.items()
                   if domain_identifier is None or key == domain_identifier or key in domain_identifier]

        where_clause = ' AND'.join([f"{key} = %s" for key, value in filters])
        select_query = f"SELECT id, {columns} FROM {table} WHERE {where_clause};"

        values_tuple = tuple(values_dict.values())

        insert_query = f"""
        INSERT IGNORE INTO {table}
        ({columns})
        VALUES ({', '.join(['%s'] * len(values_dict))})
        """

        with self._connection.cursor() as cursor:
            self._logger.info(f"Selecting the id of one of the {table}...")
            select_query_values = tuple(value for __, value in filters)
            self._logger.debug(f"Query: {select_query} - Values: {select_query_values}")
            cursor.execute(select_query, select_query_values)
            result = cursor.fetchone()
            self._logger.debug(f"Result of the query: {result}")

            if result:
                row_id, *other_values = result
                differences = [other_value != values_tuple[i] for i, other_value in enumerate(other_values)]

                if any(differences):
                    update_query = f"""
                    UPDATE IGNORE {table}
                    SET {', '.join([f"{key} = %s" for key in values_dict.keys()])}
                    WHERE id = {row_id}
                    """

                    self._logger.info(f"There are differences between the old and the new row. About to update it...")
                    self._logger.debug(f"Query: {update_query} - Values: {values_tuple}")
                    cursor.execute(update_query, values_tuple)
                    self._connection.commit()

                return row_id

            self._logger.info(f"Inserting the new row in the table {table}...")
            self._logger.debug(f"Query: {insert_query} - Values: {values_tuple}")
            cursor.execute(insert_query, values_tuple)
            self._connection.commit()
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

        with self._connection.cursor() as cursor:
            if tab_name not in self.tabs_cache:
                self._logger.debug(f"Trying to insert a new tab {tab_name}")
                cursor.execute(insert_tabs_query, tab_name)
                self._connection.commit()

                # Selecting the id of the tab name {tab_name}
                cursor.execute(f"SELECT id FROM tabs WHERE name = '{tab_name}';")
                id_tab, = cursor.fetchone()

                self.tabs_cache.update({tab_name: id_tab})
            else:
                self._logger.debug(f"The tab {tab_name} was created before, taking the id from the cache...")
                id_tab = self.tabs_cache.get(tab_name)

            # Inserting ATTRIBUTE NAMES into attributes table
            self._logger.info(f"Inserting attributes for the tab {tab_name}...")
            values = [(attribute, id_tab) for attribute in tab_info.keys()]
            self._logger.debug(f"Query: {insert_attributes_query} - Values: {values}")
            cursor.executemany(insert_attributes_query, values)
            self._connection.commit()

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
        (id_city, id_attribute, description, attribute_value, url)
        VALUES (%s, %s, %s, %s, %s) as new
            ON DUPLICATE KEY UPDATE 
                description = new.description, attribute_value = new.attribute_value, url = new.url 
        """

        attributes = self._upsert_tab_and_attributes(tab_name, tab_info)

        with self._connection.cursor() as cursor:
            # Inserting {tab_name} ATTRIBUTE VALUES into city_attributes table
            self._logger.info(f"Inserting the value of the attributes for the tab {tab_name}...")
            values = [(id_city, id_attribute, info[0], info[1], info[2] if len(info) > 2 else None)
                      for id_attribute, attribute in attributes if (info := tab_info.get(attribute))]
            self._logger.debug(f"Query: {insert_city_attributes_query} - Values: {values}")
            cursor.executemany(insert_city_attributes_query, values)
            self._connection.commit()

    def _upsert_weather(self, id_city, details):
        """
        Given the id and the details of the city, insert all the weather information in the database..

        @param id_city: Id of the current city.
        @param details: Details of the city to take the info of the weather tab.
        """

        insert_monthly_weathers_attributes_query = """
        INSERT INTO monthly_weathers_attributes
        (id_city, id_attribute, month_number, attribute_value, description)
        VALUES (%s, %s, %s, %s, %s) as new
            ON DUPLICATE KEY UPDATE 
                attribute_value = new.attribute_value, description = new.description
        """

        tab_name = 'Weather'
        tab_info = details.get('Weather', {})

        attributes = self._upsert_tab_and_attributes(tab_name, tab_info)

        with self._connection.cursor() as cursor:
            # Inserting ATTRIBUTE VALUES into monthly_weathers_attributes table
            self._logger.info(f"Inserting the value of the attributes for the tab Weather...")
            values = [(id_city, id_attribute, i + 1, value, description)
                      for id_attribute, attribute in attributes
                      for i, (__, value, description) in enumerate(tab_info.get(attribute, []))]
            self._logger.debug(f"Query: {insert_monthly_weathers_attributes_query} - Values: {values}")
            cursor.executemany(insert_monthly_weathers_attributes_query, values)
            self._connection.commit()

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

        with self._connection.cursor() as cursor:
            self._logger.info(f"Upserting many values in the table {table}...")
            values = [(id_city,) + (tuple_of_values if isinstance(tuple_of_values, tuple) else (tuple_of_values,))
                      for tuple_of_values in values]
            self._logger.debug(f"Query: {insert_query} - Values: {values}")
            cursor.executemany(insert_query, values)
            self._connection.commit()

    def _upsert_reviews(self, id_city, details):
        select_last_published_date = f"SELECT MAX(published_date) FROM reviews WHERE id_city = {id_city}"
        with self._connection.cursor() as cursor:
            self._logger.info(f"Selecting the last published date of the reviews of the city {id_city}...")
            cursor.execute(select_last_published_date)
            (last_date,) = cursor.fetchone()

        reviews = [(desc, published_date) for (desc, published_date) in details.get('Reviews', [])
                   if not last_date or datetime.strptime(published_date, '%Y-%m-%d').date() > last_date]

        self._upsert_many('reviews', id_city, ['description', 'published_date'], reviews)

    def _insert_relationships(self, id_city, details):
        """
        Given the id of the current city and the details of it, insert the relationships between this city and the near,
        next, or similar to it.

        @param id_city: Id of the current city.
        @param details: Dictionary with all the information about the current city.
        """

        types = ['Near', 'Next', 'Similar']
        cities = list(set(reduce(lambda cities_names, key: cities_names + details.get(key, []), types, [])))

        insert_cities_query = "INSERT IGNORE INTO cities (name) VALUES (%s)"
        select_cities_query = f"SELECT id, name FROM cities WHERE name IN ({', '.join(['%s'] * len(cities))})"

        insert_cities_relationships_query = """
        INSERT IGNORE INTO cities_relationships
        (id_city, id_related_city, type)
        VALUES (%s, %s, %s)
        """

        with self._connection.cursor() as cursor:
            self._logger.info(f"Inserting cities related to the current one...")
            cursor.executemany(insert_cities_query, cities)
            self._connection.commit()

            self._logger.info(f"Selecting ids from the related cities...")
            self._logger.debug(f"Query: {select_cities_query} - Values: {cities}")
            cursor.execute(select_cities_query, cities)
            relationships = []
            for id_related, name in cursor.fetchall():
                for i, type_name in enumerate(types):
                    if name in details.get(type_name, []):
                        relationships.append((id_city, id_related, i))

            self._logger.info(f"Inserting all the city relationships...")
            self._logger.debug(f"Query: {insert_cities_relationships_query} - Values: {relationships}")
            cursor.executemany(insert_cities_relationships_query, relationships)
            self._connection.commit()

    def insert_city_info(self, details):
        """Given the details of the city, insert all the necessary rows to store it in the database."""

        # TODO avoid duplicating the logic between all the cache instances
        id_continent = self._upsert_continent_and_get_id(details)
        id_country = self._upsert_country_and_get_id(id_continent, details)

        city = {'name': details.get('city'), 'city_rank': details.get('rank'), 'id_country': id_country}
        id_city = self._upsert_and_get_id("cities", city, domain_identifier='name')

        self._upsert_key_value_tab_info(id_city, 'Scores', details.get('Scores', {}))
        self._upsert_key_value_tab_info(id_city, 'Digital Nomad Guide', details.get('DigitalNomadGuide', {}))
        self._upsert_key_value_tab_info(id_city, 'Cost of Living', details.get('CostOfLiving', {}))

        self._upsert_many('photos', id_city, ['src'], details.get('Photos', []))

        pros_and_cons = details.get('ProsAndCons')
        pros = [(pro, 'P') for pro in pros_and_cons.get('pros')]
        cons = [(con, 'C') for con in pros_and_cons.get('cons')]
        # TODO: think how to avoid inserting duplicate rows without using the description as a UNIQUE constraint
        self._upsert_many('pros_and_cons', id_city, ['description', 'type'], pros + cons)

        self._upsert_reviews(id_city, details)

        self._upsert_weather(id_city, details)

        self._insert_relationships(id_city, details)

    def filter_cities_by(self, *args, num_of_cities=None, country=None, continent=None, rank_from=None, rank_to=None,
                         sorted_by, order, **kwargs):
        """Given the filter criteria, build a query to fetch the required cities from the database."""

        where_clause = f"""
        {'WHERE' if country or continent or rank_from or rank_to else ''}
            {f"country.name = '{country}' AND " if country else ""}
            {f"continent.name = '{continent}' AND " if continent else ""}
            {f'city.city_rank >= {rank_from} AND ' if rank_from else ''}
            {f'city.city_rank <= {rank_to} AND ' if rank_to else ''}
        """

        sorting_dict = {
            'rank': 'city.city_rank',
            'name': 'city.name',
            'country': 'country.name',
            'continent': 'continent.name',
            'overall score': 'SUM(case when attribute.name LIKE \'%Overall Score\' THEN city_attribute.attribute_value END)',
            'cost': 'GROUP_CONCAT(case when attribute.name LIKE \'%Cost\' THEN city_attribute.description END)',
            'internet': 'GROUP_CONCAT(case when attribute.name LIKE \'%Internet\' THEN city_attribute.description END)',
            'fun': 'SUM(case when attribute.name LIKE \'%Fun\' THEN city_attribute.attribute_value END)',
            'safety': 'GROUP_CONCAT(case when attribute.name LIKE \'%Safety\' THEN city_attribute.description END)'
        }

        order_by_clause = f"""
        ORDER BY {sorting_dict.get(sorted_by, 'city.city_rank')} {order}
        """

        main_scores = ['Overall Score', 'Cost', 'Internet', 'Fun', 'Safety']

        main_scores_columns = [
            f"GROUP_CONCAT(case when attribute.name LIKE '%{name}' THEN city_attribute.description END) '{name}'"
            for name in main_scores]

        main_scores_filters = [f'attribute.name LIKE "%{name}"' for name in main_scores]

        query = f"""
            SELECT city.city_rank, city.name, country.name, continent.name,
                {','.join(main_scores_columns)}  
            FROM cities city
            JOIN countries country ON city.id_country = country.id
            JOIN continents continent ON country.id_continent = continent.id
            JOIN city_attributes city_attribute ON city.id = city_attribute.id_city
            JOIN attributes attribute ON city_attribute.id_attribute = attribute.id
                AND ({'OR '.join(main_scores_filters)})
            JOIN tabs tab ON attribute.id_tab = tab.id AND tab.name = 'Scores'
            {where_clause.strip().rstrip(' AND ')}
            GROUP BY city.city_rank, city.name, country.name, continent.name
            {order_by_clause}
            {f'LIMIT {num_of_cities}' if num_of_cities else ''}
            ;"""

        query = "\n".join([re.sub(" +", " ", s) for s in filter(str.strip, query.splitlines())])

        self._logger.debug(f"About to execute the filter query: {query}")

        with self._connection.cursor() as cursor:
            self._logger.info("Executing the query with all the filters...")

            cursor.execute(query)
            result = cursor.fetchall()

            self._logger.debug(f"Execution results: {result}")

        return result
