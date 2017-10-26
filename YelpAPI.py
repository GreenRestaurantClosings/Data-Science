# -*- coding: utf-8 -*-
"""
Yelp Fusion API code sample.
This program demonstrates the capability of the Yelp Fusion API
by using the Search API to query for businesses by a search term and location,
and the Business API to query additional information about the top result
from the search query.
Please refer to http://www.yelp.com/developers/v3/documentation for the API
documentation.
This program requires the Python requests library, which you can install via:
`pip install -r requirements.txt`.
Sample usage of the program:
`python sample.py --term="bars" --location="San Francisco, CA"`
"""
from __future__ import print_function

import argparse
import json
import pprint
import sys
import requests
import urllib


# # This client code can run on Python 2.x or 3.x.  Your imports can be
# # simpler if you only need one of those.

# from urllib.error import HTTPError
# from urllib.parse import quote
# from urllib.parse import urlencode


# API constants, you shouldn't have to change these.


# Defaults for our simple example.
DEFAULT_TERM = 'food'
DEFAULT_LOCATION = 'Urbana, IL'
SEARCH_LIMIT = 50

API_HOST = 'https://api.yelp.com'
SEARCH_PATH = '/v3/businesses/search'
BUSINESS_PATH = '/v3/businesses/'  # Business ID will come after slash.
BEARER_TOKEN = 'OePQCxl_gHurfG3Zh5lnVjkPwggyeU_YKtUmN-GJSwCSnqMGNKNIhVq2qHaTxDXczVh_LF99LXe_CxgsVq689bvYzGaikr-jHhcDSv7afqsW0IbJp4cOngK79J7aWXYx'

"""
Given a bearer token, send a GET request to the API.
Args:
    host (str): The domain host of the API.
    path (str): The path of the API after the domain.
    bearer_token (str): OAuth bearer token, obtained using client_id and client_secret.
    url_params (dict): An optional set of query parameters in the request.
Returns:
    dict: The JSON response from the request.
"""
def request(host, path, url_params):

    headers = {
        'Authorization': 'Bearer %s' % BEARER_TOKEN,
    }

    url = path
    print(u'Querying {0} ...'.format(url))

    response = requests.get(url)

    return response.json() #returns a dictionary?

    """Query the Search API by a search term and location.
    Args:
        term (str): The search term passed to the API.
        location (str): The search location passed to the API.
    Returns:
        dict: The JSON response from the request.
    """
def search(bearer_token, term, location):

    url_params = {
        'term': term.replace(' ', '+'),
        'location': location.replace(' ', '+'),
        'limit': SEARCH_LIMIT
    }
    return request(API_HOST, SEARCH_PATH, url_params=url_params)


    """Query the Business API by a business ID.
    Args:
        business_id (str): The ID of the business to query.
    Returns:
        dict: The JSON response from the request.
    """
def get_business(bearer_token, business_id):

    business_path = BUSINESS_PATH + business_id

    return request(API_HOST, business_path, bearer_token)


    """Queries the API by the input values from the user.
    Args:
        term (str): The search term to query.
        location (str): The location of the business to query.
    """
def query_api(term, location):

    response = search(BEARER_TOKEN, term, location)
    businesses = response.get('businesses')

    if not businesses:
        print(u'No businesses for {0} in {1} found.'.format(term, location))
        return

    # creating an array of JSON objects
    results = []
    for i in range(0, len(businesses)):
        greenStreetRest = {}
        greenStreetRest["Name"] = businesses[i]['name']
        greenStreetRest["ID"] = businesses[i]['id']
        greenStreetRest["Yelp Rating"] = businesses[i]['rating']
        greenStreetRest["YelpNumReviews"] = businesses[i]['review_count']
        results.append(greenStreetRest)
        print('{0} ---- {1}, {2}'.format(businesses[i]['id'], businesses[i]['rating'], businesses[i]['review_count']))

    jsonData = json.dumps(results)

#query_api("FOOD", "Urbana, IL")
