# Nomad List Web Scrapper

The Nomad LIst Web Scrapper, as the name states, is a program that navigates to every city on the 
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
  * [Usage](#usage)
  * [Project Status](#project-status)
  * [Roadmap](#roadmap)
  * [Authors](#authors)
  * [Support](#support)
    
## Technologies Used

- Coding Language: Python 3 🐍
- Main Packages: [requests](https://docs.python-requests.org/en/master/), 
  [bs4](https://www.crummy.com/software/BeautifulSoup/), [selenium](https://selenium-python.readthedocs.io/).

## Installation
Before running the program it is recommended that the following installation steps are carried out:

1. Clone the repo by running the following code in Git Bash
   ```bash
   gh repo clone jonatankruszewski/data-mining
   ```
2. Install the dependencies (eg: Beautiful Soup, Requests, etc) required to run the program by executing the following 
   code in the Terminal (macOS/Linux) or Command Line (Windows):
   ```bash
   pip3 install -r requirements.txt
   ```
   
### Environment Variables

You may configure an env var to make Selenium works. Selenium, in order to run, needs the path to the chrome driver 
in your computer.

For Linux users:
```bash
export CHROME_DRIVER_PATH = '/path/to/chrome/driver'
```
or
```bash
CHROME_DRIVER_PATH='/path/to/chrome/driver' python3 main.py
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
