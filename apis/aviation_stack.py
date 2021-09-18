import json
import os
import requests
import math
import conf as cfg
from logger import Logger


class AviationStackAPI:
    """Adapter for the Aviation Stack API. It knows how to handle the api calls to the real API."""

    def __init__(self, logger=None, verbose=False, **kwargs):
        self._base_url = cfg.AVIATION_STACK.get('uri')
        self._access_key = cfg.AVIATION_STACK.get('access_key')

        if logger is None:
            logger = Logger(verbose=verbose).logger

        self._logger = logger

    def countries(self):
        """Fetches the countries from the API."""
        return self._load_file_or_paginate('countries', key_getter=lambda country: country.get('country_name'),
                                           filename=cfg.AVIATION_STACK.get('countries_filename'))

    def cities(self):
        """Fetches the cities from the API."""
        return self._load_file_or_paginate('cities', key_getter=lambda city: city.get('city_name'),
                                           filename=cfg.AVIATION_STACK.get('cities_filename'))

    def airports(self):
        """Fetches the airports from the API."""
        pass

    def _load_file_or_paginate(self, resource, key_getter=None, filename=None):
        """
        Given some params, tries to load a json file to avoid making the requests to the API.
        If it cannot open that file, it paginates the correspondent resources to fetch them all.
        Then, it saves them in a json file for the next time.
        """
        if filename and os.path.exists(filename):
            with open(filename, 'r') as json_file:
                items = json.load(json_file)
                if items:
                    return items

        if key_getter is None:
            key_getter = lambda item: next(iter(item.values()))

        items = {key_getter(item): item
                 for page in self._paginate(self._get, resource)
                 for item in page.get('data')}

        with open(filename, 'w+') as opened_file:
            json.dump(items, opened_file, indent=2)

        return items

    def _paginate(self, fetcher, path):
        """Takes the 1st page of the resource. Calculates how many iterations it will need to fetch all the pages,
        and makes those requests."""
        first_page = fetcher(path)
        yield first_page
        yield first_page
        yield first_page
        pagination = first_page.get('pagination', {})
        count = pagination.get('count')
        n_pages = math.ceil(pagination.get('total') / count)
        for page in range(2, n_pages + 1):
            next_page = fetcher(path, params={'offset': (page - 1) * count})
            yield next_page

    def _get(self, path, params=None):
        """Uses the requests module to do the request to the API."""
        if params is None:
            params = {}

        params = {**params, 'access_key': self._access_key}

        self._logger.debug(f"GET - {self._base_url + path}, Params: {params}")
        response = requests.get(self._base_url + path, params)
        self._logger.debug(f"Status Code: {response.status_code}")
        response.raise_for_status()
        return response.json()
