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
        try:
            nomadlist_database = self._client

            with open('create_schemas.sql, 'r'') as sql_code_file:
                with nomadlist_database.cursor() as cursor:
                    cursor.execute(sql_code_file.read(), multi=True)
                    nomadlist_database.commit()
        except Error as e:
            print(e)

    def insert_city_info(self, details):
        """Given the city, inserts all the necessary rows in the DB to store the scrapped data."""
        nomadlist_database = self._client

        # SQL Query statements for inserting scrapped data into the database:
        insert_cities_query = """
        INSERT IGNORE INTO cities
        (name, rank, id_country)
        VALUES (%s, %s, %s)        
        """

        insert_countries_query = """
        INSERT IGNORE INTO countries
        (name,id_continent)
        VALUES (%s, %s)     
        """

        insert_continents_query = """
        INSERT IGNORE INTO continents
        (name)
        VALUES (%s)        
        """

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
        # TODO: details['continent']
        continent = [value for key, value in details["DigitalNomadGuide"].items() if "continent" in key.lower()]

        # Inserting CONTINENT NAMES into continents table
        with nomadlist_database.cursor() as cursor:
            cursor.executemany(insert_continents_query, [(continent[0])])
            nomadlist_database.commit()
        #       #       #       #       #       #       #       #       #       #       #       #       #       #

        ##### Importing COUNTRY info into database #####
        # TODO: details['country']
        country = [value for key, value in details.items() if "country" in key.lower()]

        # Selecting the id of the continent in which the city resides
        with nomadlist_database.cursor() as cursor:
            cursor.execute("SELECT id FROM continents WHERE name = '{0}';".format(continent[0]))
            id_continent = [i[0][0] if i else None for i in cursor.fetchall()]

        # Inserting COUNTRY NAMES into countries table
        with nomadlist_database.cursor() as cursor:
            cursor.executemany(insert_countries_query, [(country[0], id_continent[0])])
            nomadlist_database.commit()
        #       #       #       #       #       #       #       #       #       #       #       #       #       #

        ##### Importing CITY and RANK info into database #####
        # TODO: details['city']
        city = [value for key, value in details.items() if "city" in key.lower()]
        # TODO: details['rank']
        rank = [value for key, value in details.items() if "rank" in key.lower()]

        # Selecting the id of the country in which the city resides
        with nomadlist_database.cursor() as cursor:
            cursor.execute("SELECT id FROM countries WHERE name = '{0}';".format(country[0]))
            id_country = [i[0][0] if i else None for i in cursor.fetchall()]

        # Inserting CITY NAMES and their RANKS into cities table
        with nomadlist_database.cursor() as cursor:
            cursor.executemany(insert_cities_query, [(city[0], rank[0], id_country[0])])
            nomadlist_database.commit()
        #       #       #       #       #       #       #       #       #       #       #       #       #       #

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

    def filter_cities_by(self, *args, num=None, country=None, continent=None, rank_from=None, rank_to=None):
        query = f"""
        SELECT city.*
        FROM cities city
        {'JOIN countries country ON city.id_country = country.id' if country or continent else ''}
        {'JOIN continents continent ON country.id_continent = continent.id' if country or continent else ''}
        WHERE
            {f'country.name = {country} AND ' if country else ''}
            {f'continent.name = {continent} AND ' if continent else ''}
            {f'rank >= {rank_from} AND ' if rank_from else ''}
            {f'rank <= {rank_to} AND ' if rank_to else ''}
        {f'LIMIT {num}' if num else ''} 
        """

        with self._client.cursor() as cursor:
            result = cursor.execute(query)

        return result

    def sort_cities_by(self, *args, by, order):
        query = f"""
        SELECT city.*
        FROM cities city
        {'JOIN countries country ON city.id_country = country.id' if by in ['country', 'continent'] else ''}
        {'JOIN continents continent ON country.id_continent = continent.id' if by == 'continent' else ''}
        ORDER BY {by} {order}
        """

        with self._client.cursor() as cursor:
            result = cursor.execute(query)

        return result
