# Data Mining Project

Web Scrapper to get all the information of the cities in Nomad List.

## About the project

- Instructions attached in Instructions_CH1.pdf
- Coded with Python 3 🐍
- Main packages: requests, bs4, selenium.

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

## Roadmap

- Design db using MySQL
- Add a CLI for interacting with the scrapper
- Enrich the data using external APIs
- Deploy the code to AWS
- Build a dashboard using ReDash

## Authors
- David Demby ([@david613](https://github.com/david613))
- Jonatan Kruszewski ([@jonatankruszewski](https://github.com/jonatankruszewski))
- Kevin Szuchet ([@kevinszuchet](https://github.com/kevinszuchet))

