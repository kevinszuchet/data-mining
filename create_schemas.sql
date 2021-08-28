-- TODO: TRIGGERS FOR AUDIT INFO

CREATE DATABASE IF NOT EXISTS nomad_list;

USE nomad_list;

CREATE TABLE IF NOT EXISTS continents (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(50) UNIQUE
);

CREATE TABLE IF NOT EXISTS countries (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(50) UNIQUE,
  id_continent INT,
  FOREIGN KEY(id_continent) REFERENCES continents(id)
);

CREATE TABLE IF NOT EXISTS cities (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) UNIQUE,
  city_rank INT UNIQUE,
  id_country INT,
  FOREIGN KEY (id_country) REFERENCES countries(id)
);

CREATE TABLE IF NOT EXISTS cities_relationships (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  id_city INT,
  id_related_city INT,
  type tinyint(2) CHECK (type in (0, 1, 2)),
  FOREIGN KEY (id_related_city) REFERENCES cities(id),
  FOREIGN KEY (id_city) REFERENCES cities(id)
);

CREATE TABLE IF NOT EXISTS tabs (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) UNIQUE
);

CREATE TABLE IF NOT EXISTS attributes (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255),
  id_tab INT,
  FOREIGN KEY (id_tab) REFERENCES tabs(id),
  UNIQUE (name, id_tab)
);

CREATE TABLE IF NOT EXISTS city_attributes (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  id_city INT,
  id_attribute INT,
  value DOUBLE,
  -- description VARCHAR(),
  -- url VARCHAR(),
  FOREIGN KEY (id_city) REFERENCES cities(id),
  FOREIGN KEY (id_attribute) REFERENCES attributes(id),
  UNIQUE (id_city, id_attribute)
);

CREATE TABLE IF NOT EXISTS pros_and_cons (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  description TEXT,
  type CHAR CHECK (type in ('p', 'c')),
  id_city INT,
  FOREIGN KEY (id_city) REFERENCES cities(id)
);

CREATE TABLE IF NOT EXISTS monthly_weathers (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  month INT NOT NULL,
  id_city INT,
  FOREIGN KEY (id_city) REFERENCES cities(id)
);

CREATE TABLE IF NOT EXISTS monthly_weathers_attributes (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  id_monthly_weather INT,
  id_attribute INT,
  value VARCHAR(255),
  -- description VARCHAR(),
  FOREIGN KEY (id_attribute) REFERENCES attributes(id),
  FOREIGN KEY (id_monthly_weather) REFERENCES monthly_weathers(id)
);

CREATE TABLE IF NOT EXISTS reviews (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  description TEXT,
  review_date DATETIME,
  id_city INT,
  FOREIGN KEY (id_city) REFERENCES cities(id)
);

CREATE TABLE IF NOT EXISTS photos (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  src VARCHAR(255),
  id_city INT,
  FOREIGN KEY (id_city) REFERENCES cities(id),
  UNIQUE (id_city, src)
);
