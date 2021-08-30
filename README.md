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
    + [Command Line Interface (CLI)](#command-line-interface-(cli))
  * [Project Status](#project-status)
  * [Roadmap](#roadmap)
  * [Authors](#authors)
  * [Support](#support)
    
## Technologies Used

- Coding Language: Python 3 🐍
- Main Packages: [requests](https://docs.python-requests.org/en/master/), 
  [bs4](https://www.crummy.com/software/BeautifulSoup/), [selenium](https://selenium-python.readthedocs.io/), [argparse](https://docs.python.org/3/library/argparse.html), [PyMySQL](https://pymysql.readthedocs.io/en/latest/index.html).

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

### Environment variables

You may configure an env var to make Selenium works. Selenium, in order to run, needs the path to the chrome driver 
in your computer. Although, you can choose which MySQL host you want to use.

For Linux users:

```bash
export NOMAD_LIST_CHROME_DRIVER_PATH = '/path/to/chrome/driver'
export NOMAD_LIST_MYSQL_HOST = 'your_host'
export NOMAD_LIST_MYSQL_USER = 'your_user'
export NOMAD_LIST_MYSQL_PASSWORD = 'your_password'
export NOMAD_LIST_MYSQL_DATABASE = 'nomad_list'
```
or

```bash
NOMAD_LIST_CHROME_DRIVER_PATH='/path/to/chrome/driver' NOMAD_LIST_MYSQL_HOST='your_host' NOMAD_LIST_MYSQL_USER='your_user' NOMAD_LIST_MYSQL_PASSWORD='your_password' NOMAD_LIST_MYSQL_DATABASE='nomad_list' python3 main.py
```

For MacOs users:

```bash
brew install chromedriver

#Grant access:
xattr -d com.apple.quarantine /usr/local/bin/chromedriver
```

A better option is to create a `.env` in the root of the project to avoid passing manually each variable every time you want to run the program. You only need to set the name of the variable equals the value of it.

```
NOMAD_LIST_CHROME_DRIVER_PATH='/path/to/chrome/driver'
NOMAD_LIST_MYSQL_HOST='your_host'
NOMAD_LIST_MYSQL_USER='your_user'
NOMAD_LIST_MYSQL_PASSWORD='your_password'
NOMAD_LIST_MYSQL_DATABASE='nomad_list'
```

### Database Creation

The database can be created by two different ways. The first one, via the command line:

```
mysql -u root -p < create_schemas.sql
```

The second one, using the provided [CLI]().

```bash
python3 main.py setup-db
```

## Usage
The program can be executed by navigating to the directory where the data-mining program has been saved by running
the command:

   ```bash
   cd <directory path>
   ```

in the Terminal (macOS/Linux) or the Command LIne (Windows) and then running the following code:

   ```bash
   python3 main.py
   ```

The web scrapper can also be run by loading the _main.py_ file in a Python IDE like Pycharm or IDLE and running the 
file there.

The code in _main.py_ will call the NomadListScrapper class in _nomad_list_scrapper.py_ file, which is responsible for 
handling the scrapper in the [Nomad List](https://nomadlist.com/) website. The class NomadListScrapper creates an 
object of the CityScrapper class, which is the class that actually scrapes the information from the website, and it does
so by accessing the various scrapping functions in the TabScrapper class in _tab_scrapper.py_ file.

The web scrapper, once it has completed scrapping all the information from [Nomad List](https://nomadlist.com/), 
saves all the data to a JSON file called _data.json_. The _data.json_ file is saved in the same directory as 
_main.py_.

### Command Line Interface (CLI)
...

## Project Status
Project is: _in progress_

## Roadmap
This project is at the first check point of the roadmap and further developments will be released in the near future. 
Some the intended functionality of this program are:

- Scrape data source
- Design db using MySQL and store the data
- Add a CLI for interacting with the scrapper
- Enrich the data using external APIs
- Deploy the code to AWS
- Build a dashboard using ReDash

## Authors

- David Demby ([@david613](https://github.com/david613))
- Jonatan Kruszewski ([@jonatankruszewski](https://github.com/jonatankruszewski))
- Kevin Szuchet ([@kevinszuchet](https://github.com/kevinszuchet))

## Support
If you have any queries regarding this program, please feel free to contact one of the authors.
