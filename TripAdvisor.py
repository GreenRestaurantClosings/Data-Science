import requests
from bs4 import BeautifulSoup


tripAdvisorLink = "https://www.tripadvisor.com/RestaurantsNear-g36806-d7716227-oa%s-University_of_Illinois_at_Urbana_Champaign-Urbana_Champaign_Urbana_Illinois.html"

html_doc = requests.get(tripAdvisorLink % "").text

soup = BeautifulSoup(html_doc, "html.parser" )
last_page = 0
pages_html = []
location_name = []
location_rating = []

last_page = int(soup.find("div", {"class":"pgLinks"}).find_all('a')[-2].text)

restaurants = {}
for page in range(1, last_page + 1):
	if page != 1:
		searchNumber = 30 * page - 30
		html_doc = requests.get(tripAdvisorLink % str(searchNumber)).text
	soup = BeautifulSoup(html_doc, "html.parser" )
	for info in soup.find_all('div', {"class":"near_listing"}):
		location_name = (info.find('div', {"class":"location_name"})).find("a").text
		bubbles = " 0 out of 5 bubbles"
		if (info.find('div', {"class":"rs rating"})):
			bubbles = (info.find('div', {"class":"rs rating"})).find("span").get("alt")
		restaurants[location_name] = bubbles
	searchNumber = 30 * page - 30
	html_doc = requests.get(tripAdvisorLink % str(searchNumber)).text

print(restaurants)
