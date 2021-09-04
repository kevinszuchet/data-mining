# Nomad List Web Scrapper

The Nomad List Web Scrapper, as the name states, is a program that navigates to every city on the 
[Nomad List](https://nomadlist.com/) homepage and scraps all the information that [Nomad List](https://nomadlist.com/) 
has on each and every one of these cities. The goal of this program is to make the vast amounts of information on 
[Nomad List](https://nomadlist.com/) more accessible to the user, so that they can more easily _find the best place in 
the world to live, work and travel as a remote worker_.

The information on each city is taken from the tabs that are displayed when a city tile on the 
[Nomad List](https://nomadlist.com/) home page is selected. The tabs that are scraped are:
- Scores
- Digital Nomad Guide
- Cost of Living
- Pro and Cons
- Reviews
- Weather
- Photos
- Near
- Next
- Similar

## Table of Contents

- [Nomad List Web Scrapper](#nomad-list-web-scrapper)
  * [Technologies Used](#technologies-used)
  * [Installation](#installation)
    + [Environment Variables](#environment-variables)
    + [Database Creation](#database-creation)
  * [Usage](#usage)
    + [Command Line Interface (CLI)](#command-line-interface-(CLI))
  * [Storage](#storage)
  * [Project Status](#project-status)
  * [Roadmap](#roadmap)
  * [Authors](#authors)
  * [Support](#support)
    
## Technologies Used

- Coding Language: Python 3 🐍
- Main Packages: [requests](https://docs.python-requests.org/en/master/), 
  [bs4](https://www.crummy.com/software/BeautifulSoup/), [selenium](https://selenium-python.readthedocs.io/), [argparse](https://docs.python.org/3/library/argparse.html), [pymysql](https://pypi.org/project/PyMySQL/).

## Installation
Before running the program it is recommended that the following installation steps are carried out:

1. Clone the repo by running the following code in Git Bash
   ```bash
   gh repo clone kevinszuchet/data-mining
   ```
2. Install the dependencies (eg: Beautiful Soup, Requests, etc) required to run the program by executing the following 
   code in the Terminal (macOS/Linux) or Command Line (Windows):
   ```bash
   pip3 install -r requirements.txt
   ```   
3. If the code is not loaded on and running from a server, the user must ensure that some form of MySQL host is 
   installed and running on their computer before running the program. The following [MySQL installation guide](https://dev.mysql.com/doc/mysql-installation-excerpt/5.7/en/) should be followed in order to configure the storage properly.

### Environment variables

#### Selenium

An env var can be configured in order to make Selenium work. Selenium, in order to run, needs the path to the chrome driver 
in your computer.

For Linux users:

```bash
export NOMAD_LIST_CHROME_DRIVER_PATH = '/path/to/chrome/driver'
```
or

```bash
NOMAD_LIST_CHROME_DRIVER_PATH='/path/to/chrome/driver' python3 main.py
```

For MacOs users:

```bash
brew install chromedriver

#Grant access:
xattr -d com.apple.quarantine /usr/local/bin/chromedriver
```

#### MySQL

In order to be able to save the `nomad_list` database the user needs to input the appropriate login information
for the specific host server that they are using. The user is free to choose which MySQL host they want to use to save 
their `nomad_list` database. The login details of the host server can be saved by running the following code:

For Linux users:

```bash
export NOMAD_LIST_MYSQL_HOST = 'your_host'
export NOMAD_LIST_MYSQL_USER = 'your_user'
export NOMAD_LIST_MYSQL_PASSWORD = 'your_password'
export NOMAD_LIST_MYSQL_DATABASE = 'nomad_list'
```
or

```bash
NOMAD_LIST_MYSQL_HOST='your_host' NOMAD_LIST_MYSQL_USER='your_user' NOMAD_LIST_MYSQL_PASSWORD='your_password' NOMAD_LIST_MYSQL_DATABASE='nomad_list' python3 main.py
```

#### Environment file

A better option than running the above blocks of code is to create a `.env` in the root of the project. This will help
to avoid having to pass each variable manually every time the Nomad List scrapper is run. The user needs to only 
set the value of the variables once in the `.env` like so:

```bash
NOMAD_LIST_CHROME_DRIVER_PATH='/path/to/chrome/driver'
NOMAD_LIST_MYSQL_HOST='your_host'
NOMAD_LIST_MYSQL_USER='your_user'
NOMAD_LIST_MYSQL_PASSWORD='your_password'
NOMAD_LIST_MYSQL_DATABASE='nomad_list'
```

### Database Creation

The database can be created using one of two methods. The first method to create the database is to execute the 
following code in the MySQL Command Line:

```bash
mysql -u your_user -p your_password < create_schemas.sql
```
which runs the `create_schema.sql` file which contains the MySQL code for creating the `nomad_list` database.

The second method, is to execute the `setup-db` function provided in the command line interface [CLI](#command-line-interface-(CLI)). This can 
be done by executing the following code in the terminal/command line:

```bash
python3 main.py setup-db
```

## Usage
The Nomad List scrapper can be executed by navigating to the directory where the data-mining program has been saved and 
then running the `main.py` file. 
To navigating to the correct directory, run the following commands in the terminal (Linux/masOS) or command line (Windows):

   ```bash
   cd <directory path>
   ```

In the same Terminal/ Command Line as before, after navigating to the directory where the Nomad List scrapper 
`main.py` file is saved, the Nomad List scrapper can be run by executing the following code:

   ```bash
   python3 main.py
   ```

If the `main.py` file has been given execution permissions this command can be executed: 

   ```bash
   ./main.py --help
   ```

which will display the manual of the CLI. Alternatively, if permission has not been granted, the equivalent code can be 
run:

   ```bash
   python3 main.py --help
   ```

As mentioned above, the web scrapper can be run by loading the _main.py_ file in a Python IDE like Pycharm or IDLE and 
running the file there with a special configuration. It will need the corresponding arguments, `scrape [OPTIONS]`,
(as discussed below) in order to fetch the desired cities from [Nomad List](https://nomadlist.com/), and store them in 
the _nomad_list_ MySQL database.

The code in _main.py_ will call the NomadListScrapper class in the _nomad_list_scrapper.py_ file, which is responsible for 
handling the scrapper in the [Nomad List](https://nomadlist.com/) website. The class `NomadListScrapper` creates an 
object of the `CityScrapper` class, which is the class that actually scrapes the information from the website, and it does
so by accessing the various scrapping functions in the `TabScrapper` class in _tab_scrapper.py_ file.

The web scrapper, once it has completed scrapping all the information from [Nomad List](https://nomadlist.com/), 
saves all the data to a MySQL database _nomad_list_.

### Command Line Interface (CLI)

The command line interface grants the user much greater flexibility and functionality when it comes to using the Nomad 
List scrapper as well as scrapping [Nomad List](https://nomadlist.com/). There are 3 main methods for executing the 
Nomad List scrapper in the command line:

1. __Database setup__: Creates the necessary schemas to store the scrape data into a MySQL database.
      ```bash
      python3 main.py setup-db [-h] [--verbose]

      Options:
        -h, --help
        -v, --verbose: Enable verbosity.
      ```
2. __Scrape cities from Nomad List__: Scrap specific cities from the Nomad List website.
      ```bash
      python3 main.py scrape [-h] [--num-of-cities NUM_OF_CITIES] [--scrolls SCROLLS] [--verbose]

      optional arguments:
        -h, --help
        -n --num-of-cities:   Number of required cities.
        -s --scrolls:         Number of scrolls to make in the site to fetch the cities.
        -v --verbose:         Enable verbosity.
      ```
3. __Filter the scrapped cities__: Fetch cities stored in the `nomad_list` database that match the user specified 
      filters.
      ```bash
      python3 main.py filter [-h] [--num-of-cities NUM_OF_CITIES] [--country COUNTRY] [--continent CONTINENT]
                             [--rank-from RANK_FROM] [--rank-to RANK_TO]
                             [--sorted-by SORTING_CRITERIA] [--order SORTING_ORDER] [--verbose]

      Options:
        -h, --help
        -n, --num-of-cities:  Number of required cities.
        --country:            Name of the country.
        --continent:          Name of the continent.
        --rank-from:          From rank <rank-from>.
        --rank-to:            To rank <rank-to>.
        --sorted-by:          Sorting criteria. Default: rank.
                              {rank,name,country,continent,cost,internet,fun,safety}
        --order:              Order of sorting. Default: ASC.
                              {ASC,DESC}
        -v, --verbose:        Enable verbosity.
      ```
#### scrape
The `scrape` Command Line Function (CLF) can be executed by running the following code in the CLI:

```bash
python main.py scrape
```

The `scrape` function gives the user the capability to specify how many cities they want the scrapper to scrape.
The user can do this in one of two ways: either by specifying how many cities they want the scrapper to scrape or by
specifying how far they want the scrapper to scroll-down the [Nomad List](https://nomadlist.com/) homepage.

For example, if the user would like to specify to the Nomad List Scrapper that the number of cities it must scrape is 
10, the following code will do that:

```bash
python main.py scrape -n 10
   ```
or

```bash
python main.py scrape --num-of-cities 10
   ```

If on the other hand the user wants to scroll 5 times and take all the visible cities, then the following code would be run:

```bash
python main.py scrape -s 5 
   ```
or

```bash
python main.py scrape --scrolls 5
   ```

#### filter_by
The `filter_by` Command Line Function (CLF) can be executed by running the following code in the CLI:

```bash
python main.py filter 
   ```

The `filter` function allows the user to filter through the scrapped data stored in the _nomad_list_ database in order
to search for cities that meet specific requirements or criteria. Such requirements can be which country or continent 
the city is situated, what the rank of the city is, or what is the Cost of living for nomad.

For example, if the user wants to find which are the top 10 cities in Europe for a nomad to go to based on the overall
rank of the city, the code to implement this query is:

```bash
python main.py filter -n 10 --continent 'Europe' --sorted-by 'rank' --order 'DESC' 
``` 

#### Autocompletion

To take advantage of the autocomplete, the [`argcomplete`](https://kislyuk.github.io/argcomplete/) module was installed.

To configure it, with all the requirements installed, it is necessary to run the following commands in the terminal:

Linux:

```bash
activate-global-python-argcomplete --user

sudo mv ~/.bash_completion.d/python-argcomplete /etc/.bash_completion.d
```

It's not mandatory to move the autocompletion file to the `/etc/.bash_completion.d` directory but, this dependent on it being 
[globally accessible](https://kislyuk.github.io/argcomplete/#activating-global-completion).

After resetting the terminal, the autocomplete will be ready to be used.

## Storage

### ERD
[![Nomad List ERD](https://user-images.githubusercontent.com/31735779/132088145-5d919119-d155-42f0-ad35-6bf573c8221b.jpeg)](https://lucid.app/lucidchart/3ca812c4-bcc8-4227-b7db-d8966d1fcb74/view?page=.C-3zxKe0gpQ#)

## Project Status
Project is: _in progress_

## Roadmap
This project is at the second check point of the roadmap and further developments will be released in the near future. 
Some the intended functionality of this program are:

- Scrape data source (Checkpoint #1)
- Design db using MySQL and store the data  (Checkpoint #2)
- Add a CLI for interacting with the scrapper  (Checkpoint #2)
- Enrich the data using external APIs  (Checkpoint #3)
- Deploy the code to AWS  (Checkpoint #3)
- Build a dashboard using ReDash  (Checkpoint #4)

## Authors

- David Demby ([@david613](https://github.com/david613))
- Kevin Szuchet ([@kevinszuchet](https://github.com/kevinszuchet))

## Support
If you have any queries regarding this program, please feel free to contact one of the authors.
