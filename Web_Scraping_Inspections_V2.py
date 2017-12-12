import json
import requests
import pyrebase

# Scrapes the database of inspection reports and returns an array containing all of the 
# info that the database has on each of the restaurants.
def get_all_rest_info():
	page_link = '/restaurants/api/restaurants/?limit=100&offset=0'
	big_info_arr = []
	while True:
		# We work with 100 restaurant entries at a time.
		new_dict = requests.get('http://restaurants.cu-citizenaccess.org' + page_link).json()
		# new_dict = json.loads(data)
		# This item in the dictionary contains the link to the next set of restaurant entries.
		page_link = new_dict['meta']['next']
		# If the link is null, there is no next page and we stop scraping.
		big_info_arr += new_dict['objects']
		if page_link == None:
			break
	return big_info_arr

# Goes through the array of information, takes only restaurants in the Champaign-Urbana area, 
# and returns a dictionary that maps the restaurant's hashcode to its name and array of report scores.
def get_important_rest_info():
	info_dict = {}
	big_dict = get_all_rest_info()
	for element in big_dict:
		city = element['rest_city'].upper()
		# We want to make sure that we only look for restaurants in Champaign-Urbana.
		if city == 'URBANA' or city == 'CHAMPAIGN':
			# The street number is the part of the address before the first space.
			street_number = element['rest_address'].split()[0]
			rest_name = element['rest_name']
			# Our hashcode is the street number plus the first character of the restaurant's name.
			hash_code = street_number + rest_name[0]
			report_score_sum = 0
			num_reports = 0
			reports = element['onlinereports']
			# For each report the restaurant has had, we want to append a dictionary containing
			# the report score and the report date.
			if element['rest_closed']:
				hash_code += 'c'
			if hash_code == '105B':
				print(element)
			for report in reports:
				num_reports += 1
				report_score_sum += int(float(report['insp_score']))
			average = 100
			if num_reports != 0:
				average = report_score_sum / num_reports
			info_dict[hash_code] = [rest_name, average, num_reports]
	return info_dict

# Opens a text file with Firebase database information and sets
# the Firebase config info to the values in that file.
with open(r'C:\Users\Kieran\Data-Science\configs.txt', 'r') as f:
	config = {
		"apiKey" : f.readline().rstrip(),
		"authDomain" : f.readline().rstrip(),
		"databaseURL" : f.readline().rstrip(),
		"projectId" : f.readline().rstrip(),
		"storageBucket" : f.readline().rstrip(),
		"messagingSenderId" : f.readline().rstrip()
	}

# Gets the information from all the reports and sends it to the 
# Firebase with the given configuration. Uses the hashcode as 
# noted above.
firebase = pyrebase.initialize_app(config)
db = firebase.database()
big_dict = get_important_rest_info()
for hashcode in big_dict:
	arr = big_dict[hashcode]
	data = {"Restaurant Name": arr[0], "Average Report Score": arr[1], "Number of Reports": arr[2]}
	db.child("Restaurants").child(hashcode).update(data)


