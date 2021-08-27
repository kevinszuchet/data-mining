import pymysql
from conf import MYSQL


class MySQLConnector:
    """Class that knows how to handle the connection with MySQL."""

    def __init__(self, logger):
        self._logger = logger
        self._client = self._connection()

    # Context manager adapter?

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
            nomadlist_database = self._client

            with open('create_schemas.sql, 'r'') as sql_code_file:
                with nomadlist_database.cursor() as cursor:
                    cursor.execute(sql_code_file.read(), multi=True)
                    nomadlist_database.commit()
        except Error as e:
            print(e)

    def _upsert_and_get_id(self, table, values_dict, domain_identifier=None):
        """
            Upsert a row in a table, and returns the id of it.
            @param table str
            @param values_dict dict
            @param domain_identifier str|list|tuple

            Given the table name, the values to upsert, and the optional domain_identifier,
            tries to update the row in the table, unless it doesn't exist. If that happens, then inserts the row,
            and returns its id.
        """

        columns = ', '.join(values_dict.keys())
        print("columns", columns)

        filters = [f"{key} = '{value}'" for key, value in values_dict.items() if
                   domain_identifier is None or key == domain_identifier or key in domain_identifier]
        print("filters", filters)
        where_clause = ' AND'.join(filters)
        print("where_clause", where_clause)
        select_query = f"SELECT id, {columns} FROM {table} WHERE {where_clause};"
        print("select_query", select_query)

        values_tuple = tuple(values_dict.values())
        print("values_tuple", values_tuple)

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
            print("result", result)

            if result:
                row_id, *other_values = result
                print("row_id, *other_values", row_id, other_values)
                differences = [other_value != values_tuple[i] for i, other_value in enumerate(other_values)]
                print("differences", differences)

                if any(differences):
                    cursor.execute(update_query)
                    self._client.commit()

                return row_id

            cursor.execute(insert_query, values_tuple)
            self._client.commit()
            row_id = cursor.lastrowid

        print("row_id", row_id)
        return row_id

    def insert_city_info(self, details):
        id_continent = self._upsert_and_get_id("continents", {'name': details['continent']}, domain_identifier='name')

        country = {'name': details['country'], 'id_continent': id_continent}
        id_country = self._upsert_and_get_id("countries", country, domain_identifier='name')

        city = {'name': details['city'], 'city_rank': details['rank'], 'id_country': id_country}
        id_city = self._upsert_and_get_id("cities", city, domain_identifier='name')

        # TODO: insert tabs information

    def _insert_city_info(self, details):
        """Given the city, inserts all the necessary rows in the DB to store the scrapped data."""
        nomadlist_database = self._client

        # SQL Query statements for inserting scrapped data into the database:

        insert_city_attributes_query = """
        INSERT INTO city_attributes_
        (id_city, id_attribute, value)
        VALUES (%s, %s, %s)        
        """

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

        insert_attributes_query = """
        INSERT IGNORE INTO attributes
        (name, id_tab)
        VALUES (%s, %s)        
        """

        insert_pros_and_cons_query = """
        INSERT IGNORE INTO pros_and_cons
        (description, type, id_city)
        VALUES (%s, %s, %s)        
        """
        insert_tabs_query = """
        INSERT IGNORE INTO tabs
        (name)
        VALUES (%s)        
        """

        ##### Importing CONTINENT info into database #####

        ##### Importing SCORES info into database #####
        # TODO: details['scores'] (same for all different tabs scrappers keys)
        scores_name = [key for key, value in details.items() if "scores" in key.lower()]

        with nomadlist_database.cursor() as cursor:
            cursor.executemany(insert_tabs_query, [(scores_name[0])])
            nomadlist_database.commit()

        scores_dict = [value for key, value in details.items() if "scores" in key.lower()]

        scores_attributes_name_list = []
        scores_attributes_value_list = []
        for attributes, values in scores_dict[0].items():
            scores_attributes_name_list.append(attributes)
            scores_attributes_value_list.append(values)

        # Selecting the id of the tab name "Scores"
        with nomadlist_database.cursor() as cursor:
            cursor.execute("SELECT id FROM tabs WHERE name = '{0}';".format(scores_name[0]))
            id_tab_scores = [i[0][0] if i else None for i in cursor.fetchall()]

        # Inserting SCORES ATTRIBUTE NAMES into attributes table
        for attribute in scores_attributes_name_list:
            with nomadlist_database.cursor() as cursor:
                cursor.executemany(insert_attributes_query, [(attribute, id_tab_scores[0])])
                nomadlist_database.commit()

        # Selecting the id of the city we are currently saving data for
        with nomadlist_database.cursor() as cursor:
            cursor.execute("SELECT id FROM cities WHERE name = '{0}';".format(city[0]))
            id_city = [i[0][0] if i else None for i in cursor.fetchall()]

        # Inserting SCORES ATTRIBUTE VALUES into city_attributes table
        counter = 0
        for value in scores_attributes_value_list:
            nomadlist_database.execute("SELECT id FROM attributes WHERE name = '{0}' AND id_tab = '{1}';"
                                       .format(scores_attributes_name_list[counter], id_tab_scores[0]))
            id_attribute = [i[0][0] if i else None for i in cursor.fetchall()]

            with nomadlist_database.cursor() as cursor:
                cursor.executemany(insert_city_attributes_query, [(id_city[0], id_attribute[0], value)])
                nomadlist_database.commit()
            counter += 1
        #       #       #       #       #       #       #       #       #       #       #       #       #       #

        ##### Importing DIGITALNOMADGUIDE info into database #####
        digitalnomadguide_name = [key for key, value in details.items() if "digitalnomadguide" in key.lower()]

        with nomadlist_database.cursor() as cursor:
            cursor.executemany(insert_tabs_query, [(digitalnomadguide_name[0])])
            nomadlist_database.commit()

        digitalnomadguide_dict = [value for key, value in details.items() if "digitalnomadguide" in key.lower()]

        digitalnomadguide_attributes_name_list = []
        digitalnomadguide_attributes_value_list = []
        for attributes, values in digitalnomadguide_dict[0].items():
            digitalnomadguide_attributes_name_list.append(attributes)
            digitalnomadguide_attributes_value_list.append(values)

        # Selecting the id of the tab name "Digital Nomad Guide"
        with nomadlist_database.cursor() as cursor:
            cursor.execute("SELECT id FROM tabs WHERE name = '{0}';".format(digitalnomadguide_name[0]))
            id_tab_digitalnomadguide = [i[0][0] if i else None for i in cursor.fetchall()]

        # Inserting DIGITALNOMADGUIDE ATTRIBUTE NAMES into attributes table
        for attribute in digitalnomadguide_attributes_name_list:
            with nomadlist_database.cursor() as cursor:
                cursor.executemany(insert_attributes_query, [(attribute, id_tab_digitalnomadguide[0])])
                nomadlist_database.commit()

        # Inserting DIGITALNOMADGUIDE ATTRIBUTE VALUES into city_attributes table
        counter = 0
        for value in digitalnomadguide_attributes_value_list:
            nomadlist_database.execute("SELECT id FROM attributes WHERE name = '{0}' AND id_tab = '{1}';"
                                       .format(digitalnomadguide_attributes_name_list[counter],
                                               id_tab_digitalnomadguide[0]))
            id_attribute = [i[0][0] if i else None for i in cursor.fetchall()]

            with nomadlist_database.cursor() as cursor:
                cursor.executemany(insert_city_attributes_query, [(id_city[0], id_attribute[0], value)])
                nomadlist_database.commit()
            counter += 1
        #       #       #       #       #       #       #       #       #       #       #       #       #       #

        ##### Importing REVIEWS info into database #####
        reviews_value_list = [value for key, value in details.items() if "reviews" in key.lower()]

        # Inserting REVIEWS VALUES/DESCRIPTIONS into reviews table
        for value in reviews_value_list:
            with nomadlist_database.cursor() as cursor:
                cursor.executemany(insert_reviews_query, [(id_city[0], value)])
                nomadlist_database.commit()
        #       #       #       #       #       #       #       #       #       #       #       #       #       #

        ##### Importing PHOTOS info into database #####
        photos_src_list = [value for key, value in details.items() if "photos" in key.lower()]

        # Inserting PHOTOS VALUES/SRC into photos table
        for src in photos_src_list:
            with nomadlist_database.cursor() as cursor:
                cursor.executemany(insert_photos_query, [(id_city[0], src)])
                nomadlist_database.commit()
        #       #       #       #       #       #       #       #       #       #       #       #       #       #

        ##### Importing WEATHER info into database #####
        weather_name = [key for key, value in details.items() if "weather" in key.lower()]

        with nomadlist_database.cursor() as cursor:
            cursor.executemany(insert_tabs_query, [(weather_name[0])])
            nomadlist_database.commit()

        weather_dict = [value for key, value in details.items() if "weather" in key.lower()]

        weather_attributes_name_list = []
        weather_attributes_list_of_values_lists = []
        for attributes, values in weather_dict[0].items():
            weather_attributes_name_list.append(attributes)
            weather_attributes_list_of_values_lists.append(values)

        # Selecting the id of the tab name "Weather"
        with nomadlist_database.cursor() as cursor:
            cursor.execute("SELECT id FROM tabs WHERE name = '{0}';".format(weather_name[0]))
            id_tab_weather = [i[0][0] if i else None for i in cursor.fetchall()]

        # Inserting WEATHER ATTRIBUTE NAMES (ie: Table Row Titles) into attributes table
        for attribute in weather_attributes_name_list:
            with nomadlist_database.cursor() as cursor:
                cursor.executemany(insert_attributes_query, [(attribute, id_tab_weather[0])])
                nomadlist_database.commit()

        # Inserting WEATHER MONTHS (ie: Table Column Titles) into monthly_weathers table
        for list_of_month_and_value in weather_attributes_list_of_values_lists[0]:
            month = list_of_month_and_value[0]
            with nomadlist_database.cursor() as cursor:
                cursor.executemany(insert_monthly_weathers_query, [(id_city[0], month)])
                nomadlist_database.commit()

        # Inserting WEATHER ATTRIBUTE VALUES into monthly_weathers_attributes table
        counter = 0
        for list_of_months_and_values in weather_attributes_list_of_values_lists:
            # Selecting the id of the weather attribute "Feels, Real, Humidity,etc"
            nomadlist_database.execute("SELECT id FROM attributes WHERE name = '{0}' AND id_tab = '{1}';"
                                       .format(weather_attributes_name_list[counter],
                                               id_tab_weather[0]))
            id_attribute = [i[0][0] if i else None for i in cursor.fetchall()]

            for list_of_month_and_value in list_of_months_and_values:
                month = list_of_month_and_value[0]
                value = list_of_month_and_value[1]

                # Selecting the id of the weather month "Jan, Feb, March, etc"
                with nomadlist_database.cursor() as cursor:
                    cursor.execute("SELECT id FROM monthly_weathers WHERE month = '{0}';".format(month))
                    id_monthly_weather = [i[0][0] if i else None for i in cursor.fetchall()]

                with nomadlist_database.cursor() as cursor:
                    cursor.executemany(insert_monthly_weathers_attributes_query,
                                       [(id_monthly_weather[0], id_attribute[0], value)])
                    nomadlist_database.commit()

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
            with nomadlist_database.cursor() as cursor:
                cursor.executemany(insert_photos_query, [(id_city[0], src)])
                nomadlist_database.commit()
        #       #       #       #       #       #       #       #       #       #       #       #       #       #
        # TODO: I STILL NEED TO DO STORAGE OF PROS AND CONS
        ##### Importing PROS AMD CONS info into database #####

# def main():
#
#
#
# if __name__ == "__main__":
#     main()
