import pymysql
from conf import MYSQL


class MySQLConnector:
    """Class that knows how to handle the connection with MySQL."""

    def __init__(self, logger):
        # TODO: singleton to save the ids of the tabs in a Class dict
        # self._logger = logger
        self._client = self._connection()

    @staticmethod
    def _connection():
        """Knows how to connect to the MySQL Database."""
        conn_info = {'host': MYSQL['host'], 'user': MYSQL['user'], 'password': MYSQL['password'],
                     'database': MYSQL['database']}
        return pymysql.connect(**conn_info)

    def _create_database(self):
        """Creates the MySQL Nomadlist Schema in which to store all the scrapped data."""
        # CLI: mysql -u root -p < create_schemas.sql
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
            cursor.execute(select_query)
            result = cursor.fetchone()

            if result:
                row_id, *other_values = result
                differences = [other_value != values_tuple[i] for i, other_value in enumerate(other_values)]

                if any(differences):
                    cursor.execute(update_query)
                    self._client.commit()

                return row_id

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
            cursor.execute(insert_tabs_query, tab_name)
            self._client.commit()

            # Selecting the id of the tab name {tab_name}
            cursor.execute(f"SELECT id FROM tabs WHERE name = '{tab_name}';")
            id_tab, = cursor.fetchone()

            # Inserting ATTRIBUTE NAMES into attributes table
            cursor.executemany(insert_attributes_query, [(attribute, id_tab) for attribute in tab_info.keys()])
            self._client.commit()

            # Selecting the ids of the ATTRIBUTE NAMES
            cursor.execute(f"SELECT id, name FROM attributes WHERE id_tab = '{id_tab}';")
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
            # TODO: what do happen with emojis?
            values = [(id_city, id_attribute, tab_info[attribute]) for id_attribute, attribute in attributes]
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
            values = [(id_city, id_attribute, i + 1, value)
                      for id_attribute, attribute in attributes
                      for i, [__, value] in enumerate(tab_info[attribute])]
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
            cursor.executemany(insert_query, [(id_city, *(tuple_of_values, )) for tuple_of_values in values])
            self._client.commit()

    def insert_city_info(self, details):
        id_continent = self._upsert_and_get_id("continents", {'name': details['continent']}, domain_identifier='name')

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

    def _insert_city_info(self, details):
        """Given the city, inserts all the necessary rows in the DB to store the scrapped data."""

        # SQL Query statements for inserting scrapped data into the database:

        insert_cities_relationships_query = """
        INSERT INTO cities_relationships
        (id_city, id_related_city, type)
        VALUES (%s, %s, %s)        
        """

        # TODO: I STILL NEED TO DO STORAGE OF CITY RELATIONSHIPS
        ##### Importing NEAR, NEXT and SIMILAR info into database #####
        near_name = [key for key, value in details.items() if "near" in key.lower()]
        near_values_list = [value for key, value in details.items() if "near" in key.lower()]

        next_name = [key for key, value in details.items() if "next" in key.lower()]
        next_values_list = [value for key, value in details.items() if "next" in key.lower()]

        similar_name = [key for key, value in details.items() if "similar" in key.lower()]
        similar_values_list = [value for key, value in details.items() if "similar" in key.lower()]