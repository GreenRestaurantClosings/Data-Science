# -*- coding: utf-8 -*-

import requests
import json

# Defaults for our simple example.
DEFAULT_TERM = 'food'
DEFAULT_LOCATION = 'Urbana, IL'
SEARCH_LIMIT = 50

API_HOST = 'https://api.yelp.com'
SEARCH_PATH = '/v3/businesses/search'
BUSINESS_PATH = '/v3/businesses/'  # Business ID will come after slash.
BEARER_TOKEN = ""
config = {}
with open('FinalFireBasePush.txt') as data_file:
    data = json.load(data_file)
    BEARER_TOKEN = data["bearer_token"]
    config = data["config"]

"""Query the Search API by a search term and location.
    Args:
        term (str): The search term passed to the API.
        location (str): The search location passed to the API.
    Returns:
        dict: The JSON response from the request.
"""
def search(term, location):

    url_params = {
        'term': term.replace(' ', '+'),
        'location': location.replace(' ', '+'),
        'limit': SEARCH_LIMIT
    }
    headers = {
        'Authorization': 'Bearer %s' % BEARER_TOKEN,
    }
    url = API_HOST+SEARCH_PATH
    
    response = requests.get(url, headers=headers, params=url_params)

    return response.json()


    """Queries the API by the input values from the user.
    Args:
        term (str): The search term to query.
        location (str): The location of the business to query.
    """
def query_api(term, location):

    response = search(term, location)
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

query_api("food", "Urbana, IL")