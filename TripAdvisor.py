from pyrebase import pyrebase
import requests
import json
from bs4 import BeautifulSoup


tripAdvisorLink = "https://www.tripadvisor.com/RestaurantsNear-g36806-d7716227-oa%s-University_of_Illinois_at_Urbana_Champaign-Urbana_Champaign_Urbana_Illinois.json"

html_doc = requests.get(tripAdvisorLink % "").text

soup = BeautifulSoup(html_doc, "html.parser" )
last_page = 0
pages_html = []
location_name = []
location_rating = []

last_page = int(soup.find("div", {"class":"pgLinks"}).find_all('a')[-2].text)

info = []
for page in range(1, last_page + 1):
	if page != 1:
		searchNumber = 30 * page - 30
		html_doc = requests.get(tripAdvisorLink % str(searchNumber)).text
	soup = BeautifulSoup(html_doc, "html.parser" )
	for findings in soup.find_all('div', {"class":"near_listing"}):
		location_name = (findings.find('div', {"class":"location_name"})).find("a").text
		bubbles = "0 out of 5 bubbles"
		if (findings.find('div', {"class":"rs rating"})):
			bubbles = (findings.find('div', {"class":"rs rating"})).find("span").get("alt")
		num_reviews = "0 reviews"
		if (findings.find('div', {"class":"rs rating"})):
			num_reviews = (findings.find('div', {"class":"rs rating"})).find("a").text
		restaurant = {
			"name": location_name,
			"rating": bubbles,
			"reviews": num_reviews
		}
		info.append(restaurant)
print(info)

config = {}

with open("configs.txt") as configs:
	data = json.load(configs)
	config = data["config"]

firebase = pyrebase.initialize_app(config)
db = firebase.database()
for i in info:
	data = {"Restaurant Name": i["name"], "Trip Advisor Rating": i["rating"], "Number of Reviews": i["reviews"]}
	db.child("TripAdvisor Restaurants").push(data)
