# -*- coding: utf-8 -*-

import requests
import json
from pyrebase import pyrebase

# Defaults for our simple example.
#DEFAULT_TERM = 'food'
#DEFAULT_LOCATION = 'Urbana, IL'
SEARCH_LIMIT = 50
OFFSET = 0
API_HOST = 'https://api.yelp.com'
SEARCH_PATH = '/v3/businesses/search'
BUSINESS_PATH = '/v3/businesses/'  #Business ID will come after slash.
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
def search(term, location, offset):

    url_params = {
        'term': term.replace(' ', '+'),
        'location': location.replace(' ', '+'),
        'limit': SEARCH_LIMIT,
        'offset': offset
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
def query_api(term, location, offset):
    
    response = search(term, location, offset)
    businesses = response.get('businesses')

    if not businesses:
        print(u'No businesses for {0} in {1} found.'.format(term, location))
        return

    # creating an array of JSON objects
    results = []
    for i in range(0, len(businesses)):
        greenStreetRest = {}
        greenStreetRest["Location"] = location
        greenStreetRest["Restaurant Name"] = businesses[i]['name']
        greenStreetRest["Yelp Rating"] = businesses[i]['rating']
        greenStreetRest["YelpNumReviews"] = businesses[i]['review_count']
        line1 = businesses[i]['location']['address1']
        if (line1 == None):
            line1 = "NoAddress Oops"
        greenStreetRest["key"] = line1[:line1.index(" ")] + businesses[i]['name'][0]
        results.append(greenStreetRest)
        print('{0} ---- {1}, {2}, {3}'.format(businesses[i]['review_count'], businesses[i]['rating'], businesses[i]['review_count'], greenStreetRest["key"]))
    
    return results


firebase = pyrebase.initialize_app(config)
results = query_api('restaurant', 'Urbana, IL', OFFSET)
while (len(results) >= 50):
    for element in results:
        db = firebase.database().child("Restaurants").child(element["key"])
        db.update(element)
    OFFSET += SEARCH_LIMIT
    results = query_api('restaurant', 'Urbana, IL', OFFSET)   
    

