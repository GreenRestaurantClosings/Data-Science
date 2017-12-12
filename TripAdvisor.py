from pyrebase import pyrebase
import requests
import json
from bs4 import BeautifulSoup

#general link, replace % according to page number
tripAdvisorLink = "https://www.tripadvisor.com/RestaurantsNear-g36806-d7716227-oa%s-University_of_Illinois_at_Urbana_Champaign-Urbana_Champaign_Urbana_Illinois.json"

#gets the webpage, creates Response object html_doc
html_doc = requests.get(tripAdvisorLink % "").text

soup = BeautifulSoup(html_doc, "html.parser" )
last_page = 0
pages_html = []
location_name_arr = []
location_rating = []

#determine last page number
last_page = int(soup.find("div", {"class":"pgLinks"}).find_all('a')[-2].text)

info = []
locations = []
closed = []
#loop through pages
for page in range(1, last_page + 1):
	if page != 1:
		searchNumber = 30 * page - 30
		html_doc = requests.get(tripAdvisorLink % str(searchNumber)).text
	soup = BeautifulSoup(html_doc, "html.parser" )
	for findings in soup.find_all('div', {"class":"near_listing"}):
		location_name = (findings.find('div', {"class":"location_name"})).find("a").text
		location_name_arr.append(location_name)

		#for if there are no ratings for the restaurant
		bubbles = "0 out of 5 bubbles"
		if (findings.find('div', {"class":"rs rating"})):
			bubbles = (findings.find('div', {"class":"rs rating"})).find("span").get("alt")

		#for if there are no ratings for the restaurant
		num_reviews = "0 reviews"
		if (findings.find('div', {"class":"rs rating"})):
			num_reviews = (findings.find('div', {"class":"rs rating"})).find("a").text
		locations.append((findings.find('div', {"class":"address_box"})).find('span', {"class":"format_address"}).text.replace(' ', ''))

		#open links to each specific restaurant to determine if it is closed by looking at the header
		link = findings.find('div', {'class':'location_name'}).find('a').get('href')
		html_doc2 = requests.get("https://www.tripadvisor.com" + link).text
		soup2 = BeautifulSoup(html_doc2, "html.parser")
		for findings2 in soup2.find_all('div', {"class":"ppr_rup ppr_priv_location_detail_header"}):
			#true if header determining closure is found
			if (findings2.find('h1', {'class':'heading_title closed'})):
				status = True
				closed.append('c')
			else:
				status = False
				closed.append('')

		#dictionary holding information
		restaurant = {
                        "name": location_name,
                        "rating": bubbles,
                        "reviews": num_reviews,
						"closed": status
        }

		#append each dicionary to list info
		info.append(restaurant)

#create keys for data formatted address number + first letter of restaurant name + 'c' if closed
keys = []
for location in range(len(locations)):
	end = 0
	while (locations[location])[end].isdigit() == True:
		end += 1
	locations[location] = (locations[location])[:end] + (location_name_arr[location])[0] + closed[location]
	keys.append(locations[location])

#push data to firebase
config = {}

#authentication
with open("configs.txt") as configs:
	data = json.load(configs)
	config = data["config"]

firebase = pyrebase.initialize_app(config)
db = firebase.database

#push data under keys
#loop through list of dictionaries
for i in info:
	data = {"Restaurant Name": i["name"], "Trip Advisor Rating": i["rating"], "Trip Advisor Number of Reviews": i["reviews"], "Closed": i["closed"]}
	db.child("Restaurants").child(keys[info.index(i)]).update(data)
