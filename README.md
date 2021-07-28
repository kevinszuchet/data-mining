# Data Mining Project

Web Scrapper to get all the information of the cities in [Nomad List](https://nomadlist.com/). 
The goal is to _find the best place in the world to live, work and travel as a remote worker_.

## About the project

- Coded with Python 3 🐍
- Main packages: [requests](https://docs.python-requests.org/en/master/), [bs4](https://www.crummy.com/software/BeautifulSoup/), [selenium](https://selenium-python.readthedocs.io/).

## Getting Started

1. Clone the repo

   ```bash
   gh repo clone jonatankruszewski/data-mining
   ```

2. Install dependencies

   ```bash
   pip3 install -r requirements.txt
   ```

3. Run the scrapper

   ```bash
   python3 main.py
   ```

### Environment Variables

You may configure an env var to make Selenium works. It needs the path to the chrome driver in your computer.

For Linux users:

```bash
export CHROME_DRIVER_PATH = '/path/to/chrome/driver'
```

or

```bash
CHROME_DRIVER_PATH='/path/to/chrome/driver' python3 main.py
```

For MacOs users:

```bash
brew install chromedriver

#Grant access:
xattr -d com.apple.quarantine /usr/local/bin/chromedriver
```

## Roadmap

- Scrape data source
- Design db using MySQL and store the data
- Add a CLI for interacting with the scrapper
- Enrich the data using external APIs
- Deploy the code to AWS
- Build a dashboard using ReDash

## Time required

The scrapping might take about 11 minutes on a MacBook Pro 2019. About 8 if the HTML has already been fetched.
Times might defer according to your setup.

## Authors

- David Demby ([@david613](https://github.com/david613))
- Jonatan Kruszewski ([@jonatankruszewski](https://github.com/jonatankruszewski))
- Kevin Szuchet ([@kevinszuchet](https://github.com/kevinszuchet))
