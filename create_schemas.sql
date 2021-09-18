DROP DATABASE IF EXISTS nomad_list;
CREATE DATABASE IF NOT EXISTS nomad_list;

USE nomad_list;

CREATE TABLE IF NOT EXISTS continents (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(50) UNIQUE,
  created_on DATETIME NOT NULL DEFAULT NOW(),
  updated_on DATETIME DEFAULT NULL ON UPDATE NOW()
);

CREATE TABLE IF NOT EXISTS currencies (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(50) UNIQUE,
  code VARCHAR(10) UNIQUE,
  created_on DATETIME NOT NULL DEFAULT NOW(),
  updated_on DATETIME DEFAULT NULL ON UPDATE NOW()
);

CREATE TABLE IF NOT EXISTS countries (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(50) UNIQUE,
  id_continent INT,
  iso2 CHAR(2) UNIQUE,
  iso3 CHAR(3) UNIQUE,
  iso_numeric SMALLINT UNIQUE,
  population INT,
  id_currency INT,
  fips_code VARCHAR(10),
  phone_prefix VARCHAR(100),
  created_on DATETIME NOT NULL DEFAULT NOW(),
  updated_on DATETIME DEFAULT NULL ON UPDATE NOW(),
  FOREIGN KEY(id_continent) REFERENCES continents(id),
  FOREIGN KEY (id_currency) REFERENCES currencies(id)
);

CREATE TABLE IF NOT EXISTS cities (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) UNIQUE,
  city_rank INT,
  id_country INT,
  created_on DATETIME NOT NULL DEFAULT NOW(),
  updated_on DATETIME DEFAULT NULL ON UPDATE NOW(),
  FOREIGN KEY (id_country) REFERENCES countries(id)
);

CREATE TABLE IF NOT EXISTS cities_relationships (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  id_city INT,
  id_related_city INT,
  type tinyint(2) CHECK (type in (0, 1, 2)),
  created_on DATETIME NOT NULL DEFAULT NOW(),
  updated_on DATETIME DEFAULT NULL ON UPDATE NOW(),
  FOREIGN KEY (id_related_city) REFERENCES cities(id),
  FOREIGN KEY (id_city) REFERENCES cities(id),
  UNIQUE (id_city, id_related_city, type)
);

CREATE TABLE IF NOT EXISTS tabs (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) UNIQUE,
  created_on DATETIME NOT NULL DEFAULT NOW(),
  updated_on DATETIME DEFAULT NULL ON UPDATE NOW()
);

CREATE TABLE IF NOT EXISTS attributes (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255),
  id_tab INT,
  created_on DATETIME NOT NULL DEFAULT NOW(),
  updated_on DATETIME DEFAULT NULL ON UPDATE NOW(),
  FOREIGN KEY (id_tab) REFERENCES tabs(id),
  UNIQUE (name, id_tab)
);

CREATE TABLE IF NOT EXISTS city_attributes (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  id_city INT,
  id_attribute INT,
  attribute_value DOUBLE,
  description VARCHAR(255),
  url VARCHAR(255),
  created_on DATETIME NOT NULL DEFAULT NOW(),
  updated_on DATETIME DEFAULT NULL ON UPDATE NOW(),
  FOREIGN KEY (id_city) REFERENCES cities(id),
  FOREIGN KEY (id_attribute) REFERENCES attributes(id),
  UNIQUE (id_city, id_attribute)
);

CREATE TABLE IF NOT EXISTS pros_and_cons (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  description VARCHAR(250),
  type CHAR CHECK (type in ('p', 'c')),
  id_city INT,
  created_on DATETIME NOT NULL DEFAULT NOW(),
  updated_on DATETIME DEFAULT NULL ON UPDATE NOW(),
  FOREIGN KEY (id_city) REFERENCES cities(id),
  UNIQUE (id_city, type, description)
);

CREATE TABLE IF NOT EXISTS monthly_weathers_attributes (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  id_city INT,
  id_attribute INT,
  month_number INT,
  attribute_value VARCHAR(255),
  description VARCHAR(255),
  created_on DATETIME NOT NULL DEFAULT NOW(),
  updated_on DATETIME DEFAULT NULL ON UPDATE NOW(),
  FOREIGN KEY (id_city) REFERENCES cities(id),
  FOREIGN KEY (id_attribute) REFERENCES attributes(id),
  UNIQUE (id_city, id_attribute, month_number)
);

CREATE TABLE IF NOT EXISTS reviews (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  description TEXT,
  published_date DATE,
  id_city INT,
  created_on DATETIME NOT NULL DEFAULT NOW(),
  updated_on DATETIME DEFAULT NULL ON UPDATE NOW(),
  FOREIGN KEY (id_city) REFERENCES cities(id)
);

CREATE TABLE IF NOT EXISTS photos (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  src VARCHAR(255),
  id_city INT,
  created_on DATETIME NOT NULL DEFAULT NOW(),
  updated_on DATETIME DEFAULT NULL ON UPDATE NOW(),
  FOREIGN KEY (id_city) REFERENCES cities(id),
  UNIQUE (id_city, src)
);
