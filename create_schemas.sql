CREATE DATABASE IF NOT EXISTS `nomad_list`;

USE `nomad_list`;

CREATE TABLE IF NOT EXISTS `cities` (
  `id` int,
  `name` varchar,
  `rank` int,
  `id_country` int,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`id_country`) REFERENCES `countries`(`id`),
  UNIQUE (`name`),
  UNIQUE (`rank`)
);

CREATE TABLE IF NOT EXISTS `cities_relationships` (
  `id` int,
  `id_city` int,
  `id_related_city` int,
  `type` tinyint(2),
  PRIMARY KEY (`id`),
  FOREIGN KEY (`id_related_city`) REFERENCES `cities`(`id`),
  FOREIGN KEY (`id_city`) REFERENCES `cities`(`id`),
  CHECK (`type` in (0, 1, 2))
);

CREATE TABLE IF NOT EXISTS `tabs` (
  `id` int,
  `name` varchar,
  PRIMARY KEY (`id`),
  UNIQUE (`name`)
);

CREATE TABLE IF NOT EXISTS `pros_and_cons` (
  `id` int,
  `description` text,
  `type` char,
  `id_city` int,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`id_city`) REFERENCES `cities`(`id`),
  CHECK (`type` in ('p', 'c'))
);

CREATE TABLE IF NOT EXISTS `continents` (
  `id` int,
  `name` varchar,
  PRIMARY KEY (`id`),
  UNIQUE (`name`)
);

CREATE TABLE IF NOT EXISTS `attributes` (
  `id` int,
  `name` varchar,
  `id_tab` int,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`id_tab`) REFERENCES `tabs`(`id`),
  UNIQUE (`name`, `id_tab`)
);

CREATE TABLE IF NOT EXISTS `monthly_weathers` (
  `id` int,
  `month` int,
  `id_city` int,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`id_city`) REFERENCES `cities`(`id`)
);

CREATE TABLE IF NOT EXISTS `monthly_weathers_attributes` (
  `id` int,
  `id_monthly_weather` int,
  `id_attribute` int,
  `value` varchar,
  `description` varchar,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`id_attribute`) REFERENCES `attributes`(`id`),
  FOREIGN KEY (`id_weather`) REFERENCES `monthly_weathers`(`id`)
);

CREATE TABLE IF NOT EXISTS `reviews` (
  `id` int,
  `description` text,
  `date` datetime,
  `id_city` int,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`id_city`) REFERENCES `cities`(`id`),
);

CREATE TABLE IF NOT EXISTS `city_attributes` (
  `id` int,
  `id_city` int,
  `id_attribute` int,
  `value` double,
  `description` varchar,
  `url` varchar,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`id_city`) REFERENCES `cities`(`id`),
  FOREIGN KEY (`id_attribute`) REFERENCES `attributes`(`id`)
);

CREATE TABLE IF NOT EXISTS `photos` (
  `id` int,
  `src` varchar,
  `id_city` int,
  PRIMARY KEY (`id`)
);

CREATE TABLE IF NOT EXISTS `countries` (
  `id` int,
  `name` varchar,
  `id_continent` int,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`id_continent`) REFERENCES `continents`(`id`),
  UNIQUE (`name`)
);

