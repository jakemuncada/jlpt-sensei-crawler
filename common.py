"""
Contains the common functions used in JLPT Sensei Crawler.
"""

import requests
from bs4 import BeautifulSoup


def fetchPage(url):
    """
    Fetch the HTML page and return its soup.

    Returns:
        BeautifulSoup: The HTML page soup. None if the fetching or the parsing failed.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
    except Exception as err:  # pylint: disable=broad-except
        print(f'Failed to fetch {url}, {err}')
        return None

    try:
        soup = BeautifulSoup(response.text, 'html.parser')
    except Exception as err:  # pylint: disable=broad-except
        print(f'Failed to parse soup of {url}, {err}')
        return None

    return soup
