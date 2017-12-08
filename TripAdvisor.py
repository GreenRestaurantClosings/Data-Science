from pyrebase import pyrebase
import requests
import json
from bs4 import BeautifulSoup


tripAdvisorLink = "https://www.tripadvisor.com/RestaurantsNear-g36806-d7716227-oa%s-University_of_Illinois_at_Urbana_Champaign-Urbana_Champaign_Urbana_Illinois.json"

html_doc = requests.get(tripAdvisorLink % "").text

soup = BeautifulSoup(html_doc, "html.parser" )
last_page = 0
pages_html = []
location_name_arr = []
location_rating = []

last_page = int(soup.find("div", {"class":"pgLinks"}).find_all('a')[-2].text)

info = []
locations = []
closed = []
for page in range(1, last_page + 1):
	if page != 1:
		searchNumber = 30 * page - 30
		html_doc = requests.get(tripAdvisorLink % str(searchNumber)).text
	soup = BeautifulSoup(html_doc, "html.parser" )
	for findings in soup.find_all('div', {"class":"near_listing"}):
		location_name = (findings.find('div', {"class":"location_name"})).find("a").text
		location_name_arr.append(location_name)
		bubbles = "0 out of 5 bubbles"
		if (findings.find('div', {"class":"rs rating"})):
			bubbles = (findings.find('div', {"class":"rs rating"})).find("span").get("alt")
		num_reviews = "0 reviews"
		if (findings.find('div', {"class":"rs rating"})):
			num_reviews = (findings.find('div', {"class":"rs rating"})).find("a").text
		#info.append(restaurant)
		locations.append((findings.find('div', {"class":"address_box"})).find('span', {"class":"format_address"}).text.replace(' ', ''))
		#link = findings.find('div', {'class':'location_name'}).find('a').get('href')
		#soup2 = BeautifulSoup(link, "html.parser")
		#for findings2 in soup2.find_all('div', {"class":"near_listing"}):
			#if findings2.find('h1', {'class':'heading_title closed}) in requests.get(link).text:
				#closed.append('c')
			#else:
				#closed.append('')
		restaurant = {
                        "name": location_name,
                        "rating": bubbles,
                        "reviews": num_reviews
        }
		info.append(restaurant)
print(len(info))
keys = []
for location in range(len(locations)):
	end = 0
	while (locations[location])[end].isdigit() == True:
		end += 1
	locations[location] = (locations[location])[:end] + (location_name_arr[location])[0]
	keys.append(locations[location])
print(len(keys))

config = {}

with open("configs.txt") as configs:
	data = json.load(configs)
	config = data["config"]

firebase = pyrebase.initialize_app(config)
db = firebase.database()
for i in info:
	data = {"Restaurant Name": i["name"], "Trip Advisor Rating": i["rating"], "Trip Advisor Number of Reviews": i["reviews"]}
	db.child("Restaurants").child(keys[info.index(i)]).update(data)
