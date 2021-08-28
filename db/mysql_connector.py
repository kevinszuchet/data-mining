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

    def _upsert_key_value_tab_info(self, id_city, tab_name, tab_info):
        """
        Given the name of the table, and the values to insert, tries to insert or update the rows into the tab's table.

        @param id_city: Id of the current city.
        @param tab_name: Name of the tab.
        @param tab_info: Tab information.
        """

        insert_tabs_query = "INSERT IGNORE INTO tabs (name) VALUES (%s)"
        insert_attributes_query = "INSERT IGNORE INTO attributes (name, id_tab) VALUES (%s, %s)"
        insert_city_attributes_query = """
        INSERT INTO city_attributes
        (id_city, id_attribute, value, description, url) 
        VALUES (%s, %s, %s) as new
            ON DUPLICATE KEY UPDATE 
                value = new.value, description = new.description, url = new.url
        """

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

            # Inserting {tab_name} ATTRIBUTE VALUES into city_attributes table
            # TODO: what do happen with emojis?
            values = [(id_city, id_attribute, tab_info[attribute]) for id_attribute, attribute in attributes]
            cursor.executemany(insert_city_attributes_query, values)
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

    def _insert_city_info(self, details):
        """Given the city, inserts all the necessary rows in the DB to store the scrapped data."""

        # SQL Query statements for inserting scrapped data into the database:
        insert_photos_query = """
        INSERT INTO photos
        (id_city, src)
        VALUES (%s, %s)        
        """

        insert_reviews_query = """
        INSERT INTO reviews
        (id_city, description)
        VALUES (%s, %s)        
        """

        insert_cities_relationships_query = """
        INSERT INTO cities_relationships
        (id_city, id_related_city, type)
        VALUES (%s, %s, %s)        
        """

        insert_monthly_weathers_query = """
        INSERT INTO monthly_weathers
        (id_city, month)
        VALUES (%s, %s)        
        """

        insert_monthly_weathers_attributes_query = """
        INSERT INTO monthly_weathers_attributes
        (id_monthly_weather, id_attribute, value)
        VALUES (%s, %s, %s)        
        """


        insert_pros_and_cons_query = """
        INSERT IGNORE INTO pros_and_cons
        (description, type, id_city)
        VALUES (%s, %s, %s)        
        """
        #       #       #       #       #       #       #       #       #       #       #       #       #       #

        ##### Importing DIGITALNOMADGUIDE info into database #####
        digitalnomadguide_name = [key for key, value in details.items() if "digitalnomadguide" in key.lower()]

        with self._client.cursor() as cursor:
            cursor.executemany(insert_tabs_query, [(digitalnomadguide_name[0])])
            self._client.commit()

        digitalnomadguide_dict = [value for key, value in details.items() if "digitalnomadguide" in key.lower()]

        digitalnomadguide_attributes_name_list = []
        digitalnomadguide_attributes_value_list = []
        for attributes, values in digitalnomadguide_dict[0].items():
            digitalnomadguide_attributes_name_list.append(attributes)
            digitalnomadguide_attributes_value_list.append(values)

        # Selecting the id of the tab name "Digital Nomad Guide"
        with self._client.cursor() as cursor:
            cursor.execute("SELECT id FROM tabs WHERE name = '{0}';".format(digitalnomadguide_name[0]))
            id_tab_digitalnomadguide = [i[0][0] if i else None for i in cursor.fetchall()]

        # Inserting DIGITALNOMADGUIDE ATTRIBUTE NAMES into attributes table
        for attribute in digitalnomadguide_attributes_name_list:
            with self._client.cursor() as cursor:
                cursor.executemany(insert_attributes_query, [(attribute, id_tab_digitalnomadguide[0])])
                self._client.commit()

        # Inserting DIGITALNOMADGUIDE ATTRIBUTE VALUES into city_attributes table
        counter = 0
        for value in digitalnomadguide_attributes_value_list:
            self._client.execute("SELECT id FROM attributes WHERE name = '{0}' AND id_tab = '{1}';"
                                 .format(digitalnomadguide_attributes_name_list[counter],
                                         id_tab_digitalnomadguide[0]))
            id_attribute = [i[0][0] if i else None for i in cursor.fetchall()]

            with self._client.cursor() as cursor:
                cursor.executemany(insert_city_attributes_query, [(id_city[0], id_attribute[0], value)])
                self._client.commit()
            counter += 1
        #       #       #       #       #       #       #       #       #       #       #       #       #       #

        ##### Importing REVIEWS info into database #####
        reviews_value_list = [value for key, value in details.items() if "reviews" in key.lower()]

        # Inserting REVIEWS VALUES/DESCRIPTIONS into reviews table
        for value in reviews_value_list:
            with self._client.cursor() as cursor:
                cursor.executemany(insert_reviews_query, [(id_city[0], value)])
                self._client.commit()
        #       #       #       #       #       #       #       #       #       #       #       #       #       #

        ##### Importing PHOTOS info into database #####
        photos_src_list = [value for key, value in details.items() if "photos" in key.lower()]

        # Inserting PHOTOS VALUES/SRC into photos table
        for src in photos_src_list:
            with self._client.cursor() as cursor:
                cursor.executemany(insert_photos_query, [(id_city[0], src)])
                self._client.commit()
        #       #       #       #       #       #       #       #       #       #       #       #       #       #

        ##### Importing WEATHER info into database #####
        weather_name = [key for key, value in details.items() if "weather" in key.lower()]

        with self._client.cursor() as cursor:
            cursor.executemany(insert_tabs_query, [(weather_name[0])])
            self._client.commit()

        weather_dict = [value for key, value in details.items() if "weather" in key.lower()]

        weather_attributes_name_list = []
        weather_attributes_list_of_values_lists = []
        for attributes, values in weather_dict[0].items():
            weather_attributes_name_list.append(attributes)
            weather_attributes_list_of_values_lists.append(values)

        # Selecting the id of the tab name "Weather"
        with self._client.cursor() as cursor:
            cursor.execute("SELECT id FROM tabs WHERE name = '{0}';".format(weather_name[0]))
            id_tab_weather = [i[0][0] if i else None for i in cursor.fetchall()]

        # Inserting WEATHER ATTRIBUTE NAMES (ie: Table Row Titles) into attributes table
        for attribute in weather_attributes_name_list:
            with self._client.cursor() as cursor:
                cursor.executemany(insert_attributes_query, [(attribute, id_tab_weather[0])])
                self._client.commit()

        # Inserting WEATHER MONTHS (ie: Table Column Titles) into monthly_weathers table
        for list_of_month_and_value in weather_attributes_list_of_values_lists[0]:
            month = list_of_month_and_value[0]
            with self._client.cursor() as cursor:
                cursor.executemany(insert_monthly_weathers_query, [(id_city[0], month)])
                self._client.commit()

        # Inserting WEATHER ATTRIBUTE VALUES into monthly_weathers_attributes table
        counter = 0
        for list_of_months_and_values in weather_attributes_list_of_values_lists:
            # Selecting the id of the weather attribute "Feels, Real, Humidity,etc"
            self._client.execute("SELECT id FROM attributes WHERE name = '{0}' AND id_tab = '{1}';"
                                 .format(weather_attributes_name_list[counter],
                                         id_tab_weather[0]))
            id_attribute = [i[0][0] if i else None for i in cursor.fetchall()]

            for list_of_month_and_value in list_of_months_and_values:
                month = list_of_month_and_value[0]
                value = list_of_month_and_value[1]

                # Selecting the id of the weather month "Jan, Feb, March, etc"
                with self._client.cursor() as cursor:
                    cursor.execute("SELECT id FROM monthly_weathers WHERE month = '{0}';".format(month))
                    id_monthly_weather = [i[0][0] if i else None for i in cursor.fetchall()]

                with self._client.cursor() as cursor:
                    cursor.executemany(insert_monthly_weathers_attributes_query,
                                       [(id_monthly_weather[0], id_attribute[0], value)])
                    self._client.commit()

            counter += 1
        #       #       #       #       #       #       #       #       #       #       #       #       #       #

        # TODO: I STILL NEED TO DO STORAGE OF CITY RELATIONSHIPS
        ##### Importing NEAR, NEXT and SIMILAR info into database #####
        near_name = [key for key, value in details.items() if "near" in key.lower()]
        near_values_list = [value for key, value in details.items() if "near" in key.lower()]

        next_name = [key for key, value in details.items() if "next" in key.lower()]
        next_values_list = [value for key, value in details.items() if "next" in key.lower()]

        similar_name = [key for key, value in details.items() if "similar" in key.lower()]
        similar_values_list = [value for key, value in details.items() if "similar" in key.lower()]

        # Inserting PHOTOS VALUES/SRC into photos table
        for src in photos_src_list:
            with self._client.cursor() as cursor:
                cursor.executemany(insert_photos_query, [(id_city[0], src)])
                self._client.commit()
        #       #       #       #       #       #       #       #       #       #       #       #       #       #
        # TODO: I STILL NEED TO DO STORAGE OF PROS AND CONS
        ##### Importing PROS AMD CONS info into database #####

# def main():
#
#
#
# if __name__ == "__main__":
#     main()
